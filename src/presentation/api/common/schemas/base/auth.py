from pydantic import BaseModel, EmailStr, model_validator


PASSWORD_MIN_LENGTH = 6
PASSWORD_MAX_LENGTH = 10
PASSWORD_SPECIAL_CHARACTERS = "!@#$%^&*(),.?\":{}|<>_-+[]=\\/"


def _validate_password(password: str) -> str:
    """Validate password against project-wide complexity rules."""
    if not (PASSWORD_MIN_LENGTH <= len(password) <= PASSWORD_MAX_LENGTH):
        raise ValueError(
            f"Password must be between {PASSWORD_MIN_LENGTH} and {PASSWORD_MAX_LENGTH} characters long.",
        )

    if not any(char.isdigit() for char in password):
        raise ValueError("Password must contain at least one digit.")

    if not any(char.isupper() for char in password):
        raise ValueError("Password must contain at least one uppercase letter.")

    if not any(char in PASSWORD_SPECIAL_CHARACTERS for char in password):
        raise ValueError(
            "Password must contain at least one special character "
            f"from the following list: {PASSWORD_SPECIAL_CHARACTERS}",
        )

    return password


class RegisterSchema(BaseModel):
    """Request body schema for user registration."""
    email: EmailStr
    password: str

    @model_validator(mode="after")
    def validate_password(self) -> "RegisterSchema":
        self.password = _validate_password(self.password)
        return self


class LoginSchema(BaseModel):
    """Request body schema for user login."""
    email: EmailStr
    password: str

    @model_validator(mode="after")
    def validate_password(self) -> "LoginSchema":
        self.password = _validate_password(self.password)
        return self


class LogoutSchema(BaseModel):
    """Request body schema for user logout."""
    refresh_token: str


class UpdateAccessTokenSchema(BaseModel):
    """Request body schema for access token refresh."""

    refresh_token: str
