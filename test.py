from passlib.context import CryptContext

# Define the hash context with the same parameters used for hashing
pwd_context = CryptContext(schemes=["pbkdf2_sha256"])

# Hash the password for verification
hashed_password = "$pbkdf2-sha256$29000$cU6ptfZ.z3mvFeJcC2GM8Q$iSOs66amDgPiGWRESAGF30tsad2dPh/QRpXEzYJlhQk"

# Check if the password matches the hash
password = "Bsr_3456"
if pwd_context.verify(password, hashed_password):
    print("Password is correct!")
else:
    print("Password is incorrect!")
