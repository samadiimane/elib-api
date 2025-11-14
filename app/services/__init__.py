"""Service-layer utilities."""

from app.services.search import (
    build_ilike_pattern,
    decade_bounds,
    ilike_pattern,
    resolve_sort_key,
    validate_sort,
)
from app.services.auth import (
    ACCESS_TOKEN_ALGORITHM,
    assign_role,
    authenticate_user,
    create_access_token,
    create_user_with_password,
    decode_access_token,
    ensure_google_user,
    get_user_by_email,
    get_user_with_roles,
    hash_password,
    link_google_identity,
    remove_role,
    set_user_roles,
    validate_google_id_token,
    verify_password,
)

__all__ = [
    "build_ilike_pattern",
    "decade_bounds",
    "ilike_pattern",
    "resolve_sort_key",
    "validate_sort",
    "ACCESS_TOKEN_ALGORITHM",
    "assign_role",
    "authenticate_user",
    "create_access_token",
    "create_user_with_password",
    "decode_access_token",
    "ensure_google_user",
    "get_user_by_email",
    "get_user_with_roles",
    "hash_password",
    "link_google_identity",
    "remove_role",
    "set_user_roles",
    "validate_google_id_token",
    "verify_password",
]
