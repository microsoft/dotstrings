"""Base types for the dotstrings library."""

from typing import List


class DotStringsEntry:
    """Represents a .strings entry.

    :param key: The key for the entry
    :param value: The value for the entry
    :param comments: Any comments associated with the entry
    """

    key: str
    value: str
    comments: List[str]

    def __init__(self, key: str, value: str, comments: List[str]) -> None:
        self.key = key
        self.value = value
        self.comments = comments

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
