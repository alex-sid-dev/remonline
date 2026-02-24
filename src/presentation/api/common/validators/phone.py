import phonenumbers

from src.application.errors.client import PhoneError


def validate_phone(phone_number: str) -> str:
    try:
        clean_phone = "".join(filter(lambda x: x.isdigit() or x == "+", phone_number))
        if clean_phone.startswith("8") and len(clean_phone) == 11:
            clean_phone = "+7" + clean_phone[1:]
        parsed_number = phonenumbers.parse(clean_phone, "RU")
        if phonenumbers.is_valid_number(parsed_number):
            return phonenumbers.format_number(parsed_number, phonenumbers.PhoneNumberFormat.E164)
        else:
            raise PhoneError()

    except phonenumbers.NumberParseException:
        raise PhoneError()
