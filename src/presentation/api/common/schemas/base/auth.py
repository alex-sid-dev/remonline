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
