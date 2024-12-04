from dataclasses import dataclass
from enum import StrEnum, auto


class TokenType(StrEnum):
    """Represents the token type.

    This enum is used to represent the token type.
    Can be either "access" or "refresh".
    """

    ACCESS = auto()
    REFRESH = auto()


@dataclass
class UserToken:
    """Represents a user token.

    This model is used to store the user token information.
    """

    user_id: str
    token_type: TokenType
