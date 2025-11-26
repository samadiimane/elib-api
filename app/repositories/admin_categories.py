from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass, field
from datetime import datetime
from typing import Iterable, Sequence

from sqlalchemy import func, select
from sqlalchemy.orm import Session, load_only

from app.models.category import Category, CategoryKind
from app.models.document import Document


class CategoryAdminError(Exception):
    """Base error raised for admin category operations."""

    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


SlugPattern = re.compile(r"[^a-z0-9]+")


def slugify_value(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_value = normalized.encode("ascii", "ignore").decode("ascii")
    slug = SlugPattern.sub("-", ascii_value.lower()).strip("-")
    return slug or "category"


@dataclass
class CategoryNodeData:
    id: int
    name: str
    slug: str
    kind: CategoryKind
    parent_id: int | None
    order: int
    journal_id: int | None = None
    document_count: int | None = None
    children: list["CategoryNodeData"] | None = field(default=None)


@dataclass
class CategoryPathFragmentData:
    id: int
    slug: str
    name: str


@dataclass
class CategoryListItemData:
    id: int
    name: str
    slug: str
    kind: CategoryKind
    parent_id: int | None
    order: int
    document_count: int
    created_at: datetime
    path: Sequence[CategoryPathFragmentData]


class CategoryAdminRepository:
    """Administrative helpers for managing categories."""

    def __init__(self, session: Session):
        self._session = session

    @property
    def session(self) -> Session:
        return self._session

    # ----------------------------
    # Tree + children
    # ----------------------------

    def get_tree(
        self,
        *,
        kind: CategoryKind | None,
        max_depth: int,
        include_counts: bool,
    ) -> list[CategoryNodeData]:
        max_depth = max(1, max_depth)
        roots = self._fetch_root_categories(kind=kind)
        if not roots:
            return []

        node_map: dict[int | None, list[Category]] = {None: roots}
        parent_ids = [category.id for category in roots]
        current_depth = 1
        while current_depth < max_depth and parent_ids:
            child_map = self._fetch_children_grouped(parent_ids, kind=kind)
            if not child_map:
                break
            node_map.update(child_map)
            parent_ids = [child.id for children in child_map.values() for child in children]
            current_depth += 1

        all_ids = [category.id for categories in node_map.values() for category in categories]
        counts = self._document_counts(all_ids) if include_counts else {}

        return self._assemble_nodes(node_map, None, max_depth, counts)

    def get_children(
        self,
        parent_id: int | None,
        *,
        kind: CategoryKind | None = None,
        include_counts: bool = True,
    ) -> list[CategoryNodeData]:
        if parent_id is None:
            categories = self._fetch_root_categories(kind=kind)
        else:
            categories = self._fetch_children_grouped([parent_id], kind=kind).get(parent_id, [])
        node_map = {parent_id: categories}
        ids = [category.id for category in categories]
        counts = self._document_counts(ids) if include_counts else {}
        return self._assemble_nodes(node_map, parent_id, 1, counts)

    # ----------------------------
    # Listing / search
    # ----------------------------

    def list_categories(
        self,
        *,
        search: str | None,
        kind: CategoryKind | None,
        parent_id: int | None,
        page: int,
        page_size: int,
        sort: str,
    ) -> tuple[list[CategoryListItemData], int]:
        filters: list = []

        if search:
            pattern = f"%{search.strip().lower()}%"
            filters.append(
                func.lower(Category.name).like(pattern) | func.lower(Category.slug).like(pattern)
            )

        if kind is not None:
            filters.append(Category.kind == kind)

        if parent_id is not None:
            filters.append(Category.parent_id == parent_id)

        stmt = select(Category).options(
            load_only(
                Category.id,
                Category.name,
                Category.slug,
                Category.kind,
                Category.parent_id,
                Category.journal_id,
                Category.order_index,
                Category.created_at,
            )
        )
        count_stmt = select(func.count(Category.id))
        if filters:
            stmt = stmt.where(*filters)
            count_stmt = count_stmt.where(*filters)

        if sort == "created_at":
            stmt = stmt.order_by(Category.created_at.desc(), Category.id.asc())
        else:
            stmt = stmt.order_by(Category.name.asc(), Category.id.asc())

        offset = (page - 1) * page_size
        stmt = stmt.offset(offset).limit(page_size)

        items = self._session.execute(stmt).scalars().all()
        total = self._session.execute(count_stmt).scalar_one()

        counts = self._document_counts([item.id for item in items])
        path_cache: dict[int, Category] = {}
        results: list[CategoryListItemData] = []
        for category in items:
            path = self._build_path_fragments(category, cache=path_cache)
            results.append(
                CategoryListItemData(
                    id=category.id,
                    name=category.name,
                    slug=category.slug,
                    kind=category.kind,
                    parent_id=category.parent_id,
                    order=category.order_index,
                    document_count=counts.get(category.id, 0),
                    created_at=category.created_at,
                    path=path,
                )
            )
        return results, total

    # ----------------------------
    # Mutations
    # ----------------------------

    def create_category(
        self,
        *,
        name: str,
        slug: str | None,
        kind: CategoryKind,
        parent_id: int | None,
        order: int | None,
    ) -> Category:
        normalized_slug = slugify_value(slug or name)
        self._ensure_unique_slug(kind, normalized_slug)

        parent = self._validate_parent(kind=kind, parent_id=parent_id)

        category = Category(
            name=name.strip(),
            slug=normalized_slug,
            kind=kind,
            parent_id=parent.id if parent else None,
        )
        self._session.add(category)
        self._session.flush()

        self._apply_sibling_order(category, desired_order=order)
        return category

    def update_category(
        self,
        category_id: int,
        *,
        name: str | None = None,
        slug: str | None = None,
    ) -> Category:
        category = self._session.get(Category, category_id)
        if category is None:
            raise CategoryAdminError("Category not found.", status_code=404)

        if name is not None:
            category.name = name.strip()

        if slug is not None:
            normalized_slug = slugify_value(slug)
            if normalized_slug != category.slug:
                self._ensure_unique_slug(category.kind, normalized_slug, exclude_id=category.id)
                category.slug = normalized_slug

        return category

    def move_category(
        self,
        category_id: int,
        *,
        parent_id: int | None,
        order: int | None,
    ) -> Category:
        category = self._session.get(Category, category_id)
        if category is None:
            raise CategoryAdminError("Category not found.", status_code=404)

        target_parent = self._validate_parent(kind=category.kind, parent_id=parent_id)
        new_parent_id = target_parent.id if target_parent else None

        if new_parent_id != category.parent_id:
            self._prevent_cycles(category_id=category.id, new_parent_id=new_parent_id)
            category.parent_id = new_parent_id

        self._apply_sibling_order(category, desired_order=order)
        return category

    def reorder_siblings(self, *, parent_id: int | None, items: Sequence[tuple[int, int]]) -> None:
        sibling_stmt = select(Category.id).where(
            Category.parent_id == parent_id if parent_id is not None else Category.parent_id.is_(None)
        )
        sibling_ids = set(self._session.execute(sibling_stmt).scalars().all())
        payload_ids = {item_id for item_id, _ in items}

        if sibling_ids != payload_ids:
            raise CategoryAdminError("Reorder payload must include all siblings.", status_code=400)

        order_map = {item_id: order for item_id, order in items}

        fetch_stmt = select(Category).where(Category.id.in_(payload_ids))
        categories = self._session.execute(fetch_stmt).scalars().all()
        categories.sort(key=lambda cat: (order_map[cat.id], cat.id))

        for index, category in enumerate(categories):
            category.order_index = index

    def delete_category(self, category_id: int) -> None:
        category = self._session.get(Category, category_id)
        if category is None:
            return

        has_children = (
            self._session.execute(
                select(func.count(Category.id)).where(Category.parent_id == category.id)
            ).scalar_one()
            > 0
        )
        if has_children:
            raise CategoryAdminError(
                "Cannot delete a category that still has children.", status_code=409
            )

        doc_count = self._document_counts([category.id]).get(category.id, 0)
        if doc_count > 0:
            raise CategoryAdminError(
                "Cannot delete a category that still has documents.", status_code=409
            )

        self._session.delete(category)

    def document_count(self, category_id: int) -> int:
        return self._document_counts([category_id]).get(category_id, 0)

    # ----------------------------
    # Helpers
    # ----------------------------

    def _fetch_root_categories(self, *, kind: CategoryKind | None) -> list[Category]:
        stmt = (
            select(Category)
            .options(
                load_only(
                    Category.id,
                    Category.name,
                    Category.slug,
                    Category.kind,
                    Category.parent_id,
                    Category.journal_id,
                    Category.order_index,
                )
            )
            .where(Category.parent_id.is_(None))
            .order_by(Category.order_index.asc(), Category.id.asc())
        )
        if kind is not None:
            stmt = stmt.where(Category.kind == kind)
        return self._session.execute(stmt).scalars().all()

    def _fetch_children_grouped(
        self,
        parent_ids: list[int],
        *,
        kind: CategoryKind | None,
    ) -> dict[int, list[Category]]:
        if not parent_ids:
            return {}
        stmt = (
            select(Category)
            .options(
                load_only(
                    Category.id,
                    Category.name,
                    Category.slug,
                    Category.kind,
                    Category.parent_id,
                    Category.journal_id,
                    Category.order_index,
                )
            )
            .where(Category.parent_id.in_(parent_ids))
            .order_by(Category.order_index.asc(), Category.id.asc())
        )
        if kind is not None:
            stmt = stmt.where(Category.kind == kind)
        categories = self._session.execute(stmt).scalars().all()
        grouped: dict[int, list[Category]] = {}
        for category in categories:
            grouped.setdefault(category.parent_id, []).append(category)
        return grouped

    def _assemble_nodes(
        self,
        node_map: dict[int | None, list[Category]],
        parent_id: int | None,
        depth: int,
        counts: dict[int, int],
    ) -> list[CategoryNodeData]:
        categories = node_map.get(parent_id, [])
        nodes: list[CategoryNodeData] = []
        for category in categories:
            child_nodes = None
            if depth > 1:
                child_nodes = self._assemble_nodes(node_map, category.id, depth - 1, counts)
                if not child_nodes:
                    child_nodes = None
            nodes.append(
                CategoryNodeData(
                    id=category.id,
                    name=category.name,
                    slug=category.slug,
                    kind=category.kind,
                    parent_id=category.parent_id,
                    journal_id=category.journal_id,
                    order=category.order_index,
                    document_count=counts.get(category.id),
                    children=child_nodes,
                )
            )
        return nodes

    def _document_counts(self, ids: Iterable[int]) -> dict[int, int]:
        id_list = [category_id for category_id in ids if category_id is not None]
        if not id_list:
            return {}
        stmt = (
            select(Document.primary_category_id, func.count(Document.id))
            .where(Document.primary_category_id.in_(id_list))
            .group_by(Document.primary_category_id)
        )
        return {category_id: count for category_id, count in self._session.execute(stmt)}

    def _ensure_unique_slug(
        self,
        kind: CategoryKind,
        slug: str,
        *,
        exclude_id: int | None = None,
    ) -> None:
        stmt = select(Category.id).where(Category.kind == kind, Category.slug == slug)
        if exclude_id is not None:
            stmt = stmt.where(Category.id != exclude_id)
        exists = self._session.execute(stmt).first()
        if exists:
            raise CategoryAdminError("Slug already exists for this kind.", status_code=409)

    def _validate_parent(self, *, kind: CategoryKind, parent_id: int | None) -> Category | None:
        if parent_id is None:
            return None
        parent = self._session.get(Category, parent_id)
        if parent is None:
            raise CategoryAdminError("Parent category not found.", status_code=404)
        if parent.kind != kind:
            raise CategoryAdminError("Parent category must have the same kind.", status_code=400)
        return parent

    def _prevent_cycles(self, *, category_id: int, new_parent_id: int | None) -> None:
        if new_parent_id is None:
            return
        if new_parent_id == category_id:
            raise CategoryAdminError("A category cannot be its own parent.", status_code=409)

        descendants = self._descendant_ids(category_id)
        if new_parent_id in descendants:
            raise CategoryAdminError("Cannot move a category inside its descendants.", status_code=409)

    def _descendant_ids(self, category_id: int) -> set[int]:
        cte = (
            select(Category.id)
            .where(Category.parent_id == category_id)
            .cte(name="category_descendants", recursive=True)
        )
        cte = cte.union_all(
            select(Category.id).where(Category.parent_id == cte.c.id)
        )
        rows = self._session.execute(select(cte.c.id)).scalars().all()
        return {row for row in rows if row is not None}

    def _apply_sibling_order(self, category: Category, *, desired_order: int | None) -> None:
        stmt = select(Category).where(
            Category.parent_id == category.parent_id if category.parent_id is not None else Category.parent_id.is_(None)
        )
        siblings = self._session.execute(
            stmt.order_by(Category.order_index.asc(), Category.id.asc())
        ).scalars().all()

        siblings = [s for s in siblings if s.id != category.id]
        insert_at = len(siblings) if desired_order is None else max(0, min(desired_order, len(siblings)))
        siblings.insert(insert_at, category)

        for index, sibling in enumerate(siblings):
            sibling.order_index = index

    def _build_path_fragments(
        self,
        category: Category,
        *,
        cache: dict[int, Category],
    ) -> list[CategoryPathFragmentData]:
        fragments: list[CategoryPathFragmentData] = []
        current = category
        visited: set[int] = set()

        while current is not None and current.id not in visited:
            fragments.append(
                CategoryPathFragmentData(id=current.id, slug=current.slug, name=current.name)
            )
            visited.add(current.id)
            if current.parent_id is None:
                break
            parent = cache.get(current.parent_id)
            if parent is None:
                parent = self._session.execute(
                    select(Category).options(load_only(Category.id, Category.slug, Category.name, Category.parent_id)).where(
                        Category.id == current.parent_id
                    )
                ).scalar_one_or_none()
                if parent:
                    cache[parent.id] = parent
            current = parent

        fragments.reverse()
        return fragments


__all__ = [
    "CategoryAdminRepository",
    "CategoryAdminError",
    "slugify_value",
    "CategoryNodeData",
    "CategoryListItemData",
    "CategoryPathFragmentData",
]
