# noinspection PyPackageRequirements
import argon2

pw_hasher = argon2.PasswordHasher()


def hash_password(password: str) -> str:
    """Hash the password using the ``argon2`` algorithm

    Parameters
    ----------
    password: str
        The password to hash

    Returns
    -------
    str
        The hashed password
    """

    return pw_hasher.hash(password)


def verify_password(password: str, hashed_pw: str) -> bool:
    """Verify the password against the hashed password

    Parameters
    ----------
    password: str
        The password to verify
    hashed_pw: str
        The hashed password to verify against

    Returns
    -------
    bool
        ``True`` if the password matches the hashed password, ``False`` otherwise
    """

    try:
        pw_hasher.verify(hashed_pw, password)
        return True
    except argon2.exceptions.VerifyMismatchError:
        return False
