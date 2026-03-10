import phonenumbers

from src.application.errors.client import PhoneError


def validate_phone(phone_number: str) -> str:
    """Normalize and validate a phone number in E.164 format.

    Raises PhoneError instead of low-level exceptions for any invalid input,
    including missing (None/empty) values.
    """
    if not phone_number or not isinstance(phone_number, str):
        # Treat missing or non-string input as invalid phone
        raise PhoneError()

    try:
        clean_phone = "".join(ch for ch in phone_number if ch.isdigit() or ch == "+")
        if clean_phone.startswith("8") and len(clean_phone) == 11:
            clean_phone = "+7" + clean_phone[1:]
        parsed_number = phonenumbers.parse(clean_phone, "RU")
        if phonenumbers.is_valid_number(parsed_number):
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        else:
            raise PhoneError()

    except phonenumbers.NumberParseException:
        raise PhoneError()
