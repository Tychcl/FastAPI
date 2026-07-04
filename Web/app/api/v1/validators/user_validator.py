import re

def is_valid_username(username: str): 
    return bool(re.fullmatch(r'[a-zA-Z]+', username))

def is_valid_password(password: str):
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]).{8,}$'
    return bool(re.match(pattern, password))