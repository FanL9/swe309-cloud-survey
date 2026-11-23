"""Print a password hash for STAFF_PASSWORD_HASH.

Usage (from the app/ folder):
    python hash_password.py
Type the password when asked; it is not echoed or stored. Put the printed
hash (not the password) into the platform's secret / environment settings.
"""

import getpass

from werkzeug.security import generate_password_hash


def main():
    password = getpass.getpass("Staff password: ")
    if len(password) < 10:
        raise SystemExit("Use at least 10 characters.")
    if password != getpass.getpass("Repeat password: "):
        raise SystemExit("Passwords do not match.")
    print(generate_password_hash(password))


if __name__ == "__main__":
    main()
