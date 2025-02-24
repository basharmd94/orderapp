import secrets
import sys

def generate_secret_key():
    """Generate a secure secret key suitable for JWT signing"""
    return secrets.token_hex(32)

if __name__ == "__main__":
    secret_key = generate_secret_key()
    print("\nGenerated SECRET_KEY for your .env file:")
    print(f"SECRET_KEY={secret_key}\n")
    print("Copy this value to your .env file. Keep it secure and never share it!")