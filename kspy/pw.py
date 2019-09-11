import getpass
from passlib.hash import sha512_crypt


pw = getpass.getpass(prompt='Enter the proposed esxi password: ')
hash = sha512_crypt.encrypt(pw, rounds=5000)
print(hash)
