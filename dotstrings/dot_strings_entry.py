"""Base types for the dotstrings library."""


class DotStringsEntry:
    """Represents a .strings entry.

    :param key: The key for the entry
    :param value: The value for the entry
    :param comments: Any comments associated with the entry
    :param original_line: The original line number of the position of the key.
    """

    key: str
    value: str
    comments: list[str]
    original_line: int

    def __init__(
        self,
        key: str,
        value: str,
        comments: list[str],
        original_line: int = 0,
    ) -> None:
        self.key = key
        self.value = value
        self.comments = comments
        self.original_line = original_line

    def strings_format(self) -> str:
        """Return the entry as would be formatted in a .strings file

        :returns: The .strings representation of this entry
        """
        key_value = f'"{self.key}" = "{self.value}";'

        if len(self.comments) == 0:
            return key_value

        if len(self.comments) == 1:
            return f"/* {self.comments[0]} */\n{key_value}"

        if len(self.comments) == 2:
            return f"/* {self.comments[0]}\n   {self.comments[1]} */\n{key_value}"

        output = f"/* {self.comments[0]}\n"

        for comment in self.comments[1:-1]:
            output += f"   {comment}\n"

        output += f"   {self.comments[-1]} */\n{key_value}"

        return output

    def __repr__(self) -> str:
        """Returns a raw representation of the object which can be used to reconstruct it later.

        :returns: A raw representation of the object
        """
        return str({"key": self.key, "value": self.value, "comments": self.comments})

    def __str__(self) -> str:
        """Generate and return the string representation of the object.

        :return: A string representation of the object
        """
        return self.__repr__()

    def __hash__(self) -> int:
        """Return a hash of the object.

        :return: A hash of the object
        """
        return hash((self.key, self.value, tuple(self.comments)))

    def __eq__(self, other: object) -> bool:
        """Check if two objects are equal.

        :param other: The object to compare to
        :return: True if the objects are equal, False otherwise
        """
        if not isinstance(other, DotStringsEntry):
            return False

        return (
            self.key == other.key
            and self.value == other.value
            and self.comments == other.comments
        )
