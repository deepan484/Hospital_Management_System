import base64
import re


email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

def is_valid_email(email):
    return re.match(email_pattern, email) is not None


def load_image(image_file):
    with open(image_file, "rb") as image:
        return base64.b64encode(image.read()).decode()
