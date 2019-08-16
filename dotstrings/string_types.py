"""Base types for the dotstrings library."""

from typing import Optional


class DotStringsEntry:
    """Represents a .strings entry.

    :param key: The key for the entry
    :param value: The value for the entry
    :param comment: Any comment associated with the entry
    """

    key: str
    value: str
    comment: Optional[str]

    def __init__(self, key: str, value: str, comment: Optional[str]) -> None:
        self.key = key
        self.value = value
        self.comment = comment

    def __repr__(self) -> str:
        """Returns a raw representation of the object which can be used to reconstruct it later.

        :returns: A raw representation of the object
        """
        return str({"key": self.key, "value": self.value, "comment": self.comment})

    def __str__(self) -> str:
        """Generate and return the string representation of the object.

        :return: A string representation of the object
        """
        return str(self.__repr__())
