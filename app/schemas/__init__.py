"""Pydantic schema exports."""

from app.schemas.category import (
    CategoryChildOut,
    CategoryChildrenResponse,
    CategoryCounts,
    CategoryDetailOut,
    CategoryOut,
)
from app.schemas.document import DocumentOut, PrimaryCategoryRef
from app.schemas.author import AuthorOut
from app.schemas.pagination import PaginatedResponse
from app.schemas.search import (
    FacetCategory,
    FacetCount,
    FacetYear,
    FacetYearBucket,
    SearchDocumentsResponse,
    SearchFacets,
)
from app.schemas.event import (
    EventBaseOut,
    EventDetailOut,
    AwardDetailsOut,
    ExhibitionDetailsOut,
    SeminarDetailsOut,
    AwardWinnerOut,
    SeminarSpeakerOut,
    SeminarAgendaItemOut,
)
from app.schemas.journal import JournalOut, JournalCounts, JournalDetailOut, JournalIssueOut
from app.schemas.user import (
    AdminUserCreate,
    AdminUserOut,
    AdminUserToggleActive,
    AdminUserUpdateRoles,
    AdminUsersPage,
    AuthIdentityOut,
    AuthResponse,
    GoogleAuthRequest,
    LoginRequest,
    RoleRequest,
    TokenResponse,
    UserCreateRequest,
    UserOut,
    UserRoleOut,
)


__all__ = [
    "CategoryChildOut",
    "CategoryChildrenResponse",
    "CategoryCounts",
    "CategoryDetailOut",
    "CategoryOut",
    "DocumentOut",
    "AuthorOut",
    "PaginatedResponse",
    "PrimaryCategoryRef",
    "FacetCategory",
    "FacetCount",
    "FacetYear",
    "FacetYearBucket",
    "SearchDocumentsResponse",
    "SearchFacets",
    "JournalOut",
    "JournalCounts",
    "JournalDetailOut",
    "JournalIssueOut",
    "EventBaseOut",
    "EventDetailOut",
    "AwardDetailsOut",
    "ExhibitionDetailsOut",
    "SeminarDetailsOut",
    "AwardWinnerOut",
    "SeminarSpeakerOut",
    "SeminarAgendaItemOut",
    "AdminUserOut",
    "AdminUserCreate",
    "AdminUserUpdateRoles",
    "AdminUserToggleActive",
    "AdminUsersPage",
    "AuthIdentityOut",
    "UserRoleOut",
    "UserOut",
    "UserCreateRequest",
    "LoginRequest",
    "GoogleAuthRequest",
    "RoleRequest",
    "TokenResponse",
    "AuthResponse",
]
