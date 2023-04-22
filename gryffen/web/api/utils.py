import re


def is_valid_email(email):
    # Email validation regex pattern
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

    # Use the regex pattern to search for a match in the email string
    match = re.match(pattern, email)

    # If match is found, return True, else return False
    if match:
        return True
    else:
        return False
