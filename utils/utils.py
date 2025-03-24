import re

import requests

from configs.variables import ERROR_GROUP, ERROR_BOT


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



def error_sender(error_message):
    payload = {
        "chat_id": ERROR_GROUP,
        "text": error_message,
        "parse_mode": "HTML"
    }

    # Send the request to send the inline keyboard message
    response = requests.post(
        url=f"https://api.telegram.org/bot{ERROR_BOT}/sendMessage",
        json=payload
    )
    # Check the response status
    if response.status_code == 200:
        return response
    else:
        print("Response text: ", response.text)
        return None