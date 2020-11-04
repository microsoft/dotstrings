"""Localized string types"""

import hashlib
import re
from typing import ClassVar, List, Optional, Pattern

from dotstrings.dot_strings_entry import DotStringsEntry


class LocalizedString:
    """Represents a localized string.

    Note: Automatic key generation is supported. By this, if you pass None as
    the value for your `key`, the value will automatically be derived as a hash
    of the value and the key extension. This should normally only ever be done
    for your default language (as the key will change between languages).

    The reason we support this is that this is a useful class to use in various
    projects, not just as the result of reading .strings files. In those cases,
    you may wish to automatically generate keys to avoid having to manually
    deal with deduplication.

    :param Optional[str] key: The key for the string. If this is None, they key
                              will be automatically derived from the value and
                              the key extension.
    :param str value: The value of the string
    :param str language: The language code of the string
    :param str table: The string table to use
    :param Optional[str] comment: The comment for the string
    :param Optional[str] key_extension: The key extension to differentiate
                                        between identical strings with different
                                        meanings
    :param str bundle: The bundle the string can be found in
    """

    _TOKEN_REGEX: ClassVar[
        str
    ] = r"(%(?:[0-9]+\$)?[0-9]*\.?[0-9]*[a-zA-Z]{0,2}[dDuUxXoOfFeEgGcCsSaAp@])"
    _TOKEN_PATTERN: ClassVar[Pattern] = re.compile(_TOKEN_REGEX, flags=re.DOTALL)

    key: str
    value: str
    language: str
    table: str
    comment: Optional[str]
    key_extension: Optional[str]
    bundle: str

    def __init__(
        self,
        *,
        key: Optional[str],
        value: str,
        language: str,
        table: str,
        comment: Optional[str] = None,
        key_extension: Optional[str] = None,
        bundle: str = "",
    ) -> None:
        self.value = value
        self.language = language
        self.comment = comment
        self.key_extension = key_extension
        self.table = table
        self.bundle = bundle

        if key is not None:
            self.key = key
        else:
            self.key = LocalizedString._calculate_key(value=value, key_extension=key_extension)

    @staticmethod
    def _calculate_key(*, value: str, key_extension: Optional[str]) -> str:
        """Calculate the unique key to use for this string.

        :param value: The value of the localized string
        :param key_extension: Any key extension value to use to differentiate
                              between identical values

        :returns: The unique key for the string
        """

        # Calculate key based on string interpreted by the compiler
        hash_input = value

        if key_extension is not None:
            hash_input += ":" + key_extension

        hash_input = hash_input.replace("\\n", "\n")  # Replace "slash n" with newline character
        hash_input = hash_input.replace('\\"', '"')  # Replace "slash quote" with quote character

        key = hashlib.md5(hash_input.encode("utf-8")).hexdigest()

        return key

    def tokens(self) -> List[str]:
        """Find and return the tokens in the string.

        :returns: The list of tokens in the string
        """
        return LocalizedString._TOKEN_PATTERN.findall(self.value)

    def ns_localized_format(self) -> str:
        """Return the NSLocalizedString version of our call.

        :returns: The NSLocalizedString version of our call

        :raises Exception: If the language is not English
        """
        if self.language != "en":
            raise Exception(f"This should only be called for English strings: {self}")
        return (
            "NSLocalizedStringWithDefaultValue("
            + f'@"{self.key}", @"{self.table}", @"{self.bundle}", @"{self.value}", @"{self.comment}");'
        )

    def __eq__(self, other: object) -> bool:
        """Determine if the supplied object is equal to self

        :param other: The object to compare to self

        :returns: True if they are equal, False otherwise.
        """
        if not isinstance(other, LocalizedString):
            return False

        return (
            self.value == other.value
            and self.language == other.language
            and self.comment == other.comment
            and self.key_extension == other.key_extension
            and self.table == other.table
            and self.bundle == other.bundle
            and self.key == other.key
        )

    def __ne__(self, other: object) -> bool:
        """Determine if the supplied object is unequal to self

        :param other: The object to compare to self

        :returns: True if they are unequal, False otherwise.
        """
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Calculate the hash of the object

        :returns: The hash value of the object
        """
        return hash(
            (
                self.value,
                self.language,
                self.comment,
                self.key_extension,
                self.table,
                self.bundle,
                self.key,
            )
        )

    def __repr__(self) -> str:
        """Returns a raw representation of the object which can be used to reconstruct it later.

        :returns: A raw representation of the object
        """
        return str(
            {
                "key": self.key,
                "value": self.value,
                "language": self.language,
                "table": self.table,
                "comment": self.comment,
                "bundle": self.bundle,
                "key_extension": self.key_extension,
            }
        )

    def __str__(self) -> str:
        """Generate and return the string representation of the object.

        :return: A string representation of the object
        """
        return self.__repr__()

    @staticmethod
    def from_dotstring_entries(
        *, entries: List[DotStringsEntry], language: str, table: str
    ) -> List["LocalizedString"]:
        """Convert a list of DotStringsEntry's into a list of LocalizedString's

        :param List[DotStringsEntry] entries: The DotStringsEntry's to convert
        :param str language: The language the DotStringsEntry's are in
        :param str table: The table the DotStringsEntry's are from

        :returns: A list of LocalizedStrings
        """

        output = []

        for entry in entries:
            localized = LocalizedString(
                key=entry.key,
                value=entry.value,
                language=language,
                table=table,
                comment="\n".join(entry.comments),
                key_extension=None,
                bundle="",
            )
            output.append(localized)

        return output
