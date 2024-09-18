
from passlib.hash import pbkdf2_sha256

# Define the password
password = "123456789"

# Generate the hash
hash = "$pbkdf2-sha256$29000$ofQ.59z7/5/znnNu7f2f0w$LaxM2PRqbAYyjKDPhSSwDPfDqKqZVtlAKQUDzc4I3bk"

# Verify the hash
is_correct = pbkdf2_sha256.verify(password, hash)

print(f"Generated Hash: {hash}")
print(f"Password Verification: {'Correct' if is_correct else 'Incorrect'}")
