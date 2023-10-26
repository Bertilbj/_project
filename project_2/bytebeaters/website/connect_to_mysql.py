"""'
#-#-# DEL IKKE DENNE FIL MED ANDRE! #-#-#
Denne fil indholder secret credentials projektet.
Dette er måde encryption nøgle og MySQL credentials.
Dette er ikke en sikker måde at gemme det, men bedre
end at have det i klartekst.
"""
import contextlib

# from cryptography.fernet import Fernet
import bcrypt
import mysql.connector

# Secret Key lavet med Fernet.generate_key()
key = b'nUXVeTxCnLpjIf_xJPkhkBWqEFT2KCFxmydxs1GlxqY='

# salt = bcrypt.gensalt()
salt = b'$2b$12$VjR2N6Z56emkoc7jBiAHwe'


def secret_key():
    return key


def hash_password(password):
    return bcrypt.hashpw(password.encode(), salt)

# def encrypt_password(password):
#     # Fernet kræver en byte-string, derfor .encode()
#     return Fernet(key).encrypt(password.encode())


# def decrypt_password(password):
#     # Fernet kræver en byte-string, derfor .decode()
#     return Fernet(key).decrypt(password).decode()


@contextlib.contextmanager
# Context manager til at åbne og lukke DB connection automatisk
def open_db(db):
    # Åbner connection til DB, og lukker den igen når den er færdig med at blive brugt
    conn = mysql.connector.connect(host='bytebeaters.sof60.dk',
                                   database=db,
                                   user='bytebeaters',
                                   password='MangoLoco42',
                                   )
    try:
        """
        yield er en generator, der returnerer conn,
        og lukker den igen når den er færdig med at blive brugt.
        """
        yield conn
    finally:
        conn.close()
