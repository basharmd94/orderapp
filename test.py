
from passlib.hash import pbkdf2_sha256

# Define the password
password = "1234"

# Generate the hash
hash = pbkdf2_sha256.hash(password)

# Verify the hash
is_correct = pbkdf2_sha256.verify(password, hash)

print(f"Generated Hash: {hash}")
print(f"Password Verification: {'Correct' if is_correct else 'Incorrect'}")
