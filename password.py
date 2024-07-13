from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")


def passwordCheck(password):

    crypt = pwd_context.hash(password)
    print (crypt)

    return crypt



passwordCheck("1234")
