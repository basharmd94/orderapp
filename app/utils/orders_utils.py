# utils.py
import random
import string

def generate_random_number(length: int) -> str:
    return ''.join(random.choices(string.digits, k=length))

def format_invoice_number(invoicesl: str) -> str:
    parts = [invoicesl[i:i+5] for i in range(0, len(invoicesl), 4)]
    return '-'.join(parts)

