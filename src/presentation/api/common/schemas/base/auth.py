from pydantic import BaseModel, EmailStr, model_validator

from src.presentation.api.common.validators.password import validate_password


class RegisterSchema(BaseModel):
    """Request body schema for user registration."""

    email: EmailStr
    password: str

    @model_validator(mode="after")
    def validate_password(self) -> "RegisterSchema":
        self.password = validate_password(self.password)
        return self


class RegisterSupervisorSchema(BaseModel):
    """Request body schema for external supervisor registration."""

    email: EmailStr
    password: str
    full_name: str
    phone: str
    organization_name: str
    inn: str
    address: str | None = None
    kpp: str | None = None
    bank_account: str | None = None
    corr_account: str | None = None
    bik: str | None = None

    @model_validator(mode="after")
    def validate_password(self) -> "RegisterSupervisorSchema":
        self.password = validate_password(self.password)
        return self


class LoginSchema(BaseModel):
    """Request body schema for user login."""

    email: EmailStr
    password: str

    @model_validator(mode="after")
    def validate_password(self) -> "LoginSchema":
        self.password = validate_password(self.password)
        return self


class LogoutSchema(BaseModel):
    """Request body schema for user logout."""

    refresh_token: str


class UpdateAccessTokenSchema(BaseModel):
    """Request body schema for access token refresh."""

    refresh_token: str
