from src.presentation.api.common.validation_rules import (
    PASSWORD_MAX_LENGTH,
    PASSWORD_MIN_LENGTH,
    PASSWORD_SPECIAL_CHARACTERS,
)


def validate_password(password: str) -> str:
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