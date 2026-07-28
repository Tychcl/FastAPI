import re

def is_valid_username(username: str): 
    return bool(re.fullmatch(r'[a-zA-Z]+', username))

def is_valid_email(email: str):
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))
    
def is_valid_password(password: str):
    pattern = r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d)(?=.*[!@#$%^&*()_+\-=\[\]{};:\'",.<>/?\\|`~]).{8,}$'
    return bool(re.match(pattern, password))