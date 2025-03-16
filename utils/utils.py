import re


def format_phone_number(phone: str) -> str:
    """
    Ensures the phone number is in the format +998946104316.
    - If missing '+', it is added.
    - Must be exactly 12 digits after the country code.
    - Must start with '998'.
    """
    phone = phone.strip()
    if not phone.startswith("+"):
        phone = "+" + phone

    pattern = r"^\+998\d{9}$"
    return phone if re.fullmatch(pattern, phone) else None
