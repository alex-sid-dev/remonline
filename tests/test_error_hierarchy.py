from src.application.errors._base import (
    ApplicationError,
    AuthenticationError,
    ConflictError,
    DomainError,
    EntityNotFoundError,
    FieldError,
    PermissionDeniedError,
)
from src.application.errors.auth import (
    InvalidAccessTokenErrorPerm,
    TokenInvalidError,
    InvalidTimeZoneError,
)
from src.presentation.api.common.exc_handlers import resolve_status_code as _resolve_status_code


class TestErrorHierarchy:
    def test_application_error_is_exception(self):
        err = ApplicationError()
        assert isinstance(err, Exception)

    def test_domain_error_inherits_application(self):
        err = DomainError()
        assert isinstance(err, ApplicationError)

    def test_permission_denied_error(self):
        err = InvalidAccessTokenErrorPerm()
        assert isinstance(err, PermissionDeniedError)
        assert not isinstance(err, AuthenticationError)

    def test_invalid_timezone_is_domain_error(self):
        err = InvalidTimeZoneError()
        assert isinstance(err, DomainError)
        assert err.message == "Invalid time zone"

    def test_token_invalid_is_auth_error(self):
        err = TokenInvalidError()
        assert isinstance(err, AuthenticationError)


class TestStatusCodeMapping:
    def test_entity_not_found_maps_to_404(self):
        assert _resolve_status_code(EntityNotFoundError()) == 404

    def test_auth_error_maps_to_401(self):
        assert _resolve_status_code(AuthenticationError()) == 401

    def test_permission_denied_maps_to_403(self):
        assert _resolve_status_code(PermissionDeniedError()) == 403

    def test_conflict_maps_to_409(self):
        assert _resolve_status_code(ConflictError()) == 409

    def test_field_error_maps_to_422(self):
        assert _resolve_status_code(FieldError()) == 422

    def test_domain_error_maps_to_400(self):
        assert _resolve_status_code(DomainError()) == 400

    def test_application_error_maps_to_500(self):
        assert _resolve_status_code(ApplicationError()) == 500

    def test_permission_denied_subclass_maps_to_403(self):
        assert _resolve_status_code(InvalidAccessTokenErrorPerm()) == 403

    def test_token_invalid_maps_to_401(self):
        assert _resolve_status_code(TokenInvalidError()) == 401
