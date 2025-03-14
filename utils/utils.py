import re


def is_valid_phone_number(phone: str) -> bool:
    """
    Validates if the phone number follows the strict format: 998946104316.
    - Must be exactly 12 digits.
    - Must start with '998'.
    """
    pattern = r"^998\d{9}$"
    return bool(re.fullmatch(pattern, phone))
