"""Utilities for dealing with .strings files"""

import plistlib
import re
from typing import BinaryIO, Pattern, TextIO

from dotstrings.exceptions import DotStringsException
from dotstrings.dot_strings_entry import DotStringsEntry
from dotstrings.dot_stringsdict_entry import DotStringsDictEntry


class Patterns:
    """The patterns used by the parser."""

    comment = re.compile(
        r"(\'(?:[^\'\\]|\\[\s\S])*\')|//.*|/\*(?:[^*]|\*(?!/))*\*/", re.MULTILINE
    )
    whitespace = re.compile(r"\s*", re.MULTILINE)
    entry = re.compile(r'"(.*)"\s*=\s*"(.*)" *;')
    quoteless_key_entry = re.compile(r'(.*?)\s*=\s*"(.*)" *;')


class Scanner:
    """Regex string scanner."""

    string: str
    offset: int
    line: int

    def __init__(self, string: str) -> None:
        self.string = string
        self.offset = 0
        self.line = 0

    def has_more(self) -> bool:
        """Check if there is more string remaining.

        :returns: True if there is more string remaining, False otherwise
        """
        return self.offset < len(self.string)

    def scan(self, pattern: str | Pattern, flags: int = 0) -> str | None:
        """Scan a string for a pattern and return the string if found.

        :param pattern: The pattern to scan for
        :param flags: Any flags to use for a string pattern

        :returns: The string if the pattern matches, None otherwise.
        """

        if isinstance(pattern, str):
            _pattern = re.compile(pattern, flags)
        else:
            _pattern = pattern

        match = _pattern.match(self.string, self.offset)

        if match is None:
            return None

        self.offset = match.end()
        self.line += match.group(0).count("\n")
        return match.group(0)


def load(
    file_details: TextIO | str, encoding: str | None = None
) -> list[DotStringsEntry]:
    """Parse the contents of a .strings file from a file pointer.

    :param file_details: The file pointer or a file path
    :param encoding: The encoding the file is in

    :returns: A list of `DotStringEntry`s
    """

    # If it's a file pointer, read in the contents and parse
    if not isinstance(file_details, str):
        contents = "".join(file_details.readlines())
        return loads(contents)

    # It must have been a path instead then, so open the file, and parse
    if encoding:
        encoding_list = [encoding]
    else:
        encoding_list = ["utf-8-sig", "utf-8", "utf-16", "utf-16-le", "utf-16-be"]

    for encoding_option in encoding_list:
        try:
            with open(file_details, "r", encoding=encoding_option) as strings_file:
                return load(strings_file)
        except UnicodeDecodeError:
            pass

    raise DotStringsException(
        f"Could not determine encoding for file at path: {file_details}"
    )


def loads(contents: str) -> list[DotStringsEntry]:
    """Parse the contents of a .strings file.

    Note: CRLF is not supported in strings.

    :param contents: The contents of a .strings file

    :returns: A list of `DotStringsEntry`s"""

    # Sometimes we have CRLF. It's easier to just replace now. This could, in
    # theory, cause issues, but we just don't support it for now.
    if "\r\n" in contents:
        raise DotStringsException("Strings contain CRLF")
    contents = contents.replace("\r\n", "\n")

    scanner = Scanner(contents)

    strings = []

    # Main parse loop
    while scanner.has_more():
        # Clear any whitespace
        _ = scanner.scan(Patterns.whitespace)

        comments = []

        # Get any comment
        while True:
            comment = scanner.scan(Patterns.comment)

            # If there wasn't a comment, we can finish trying and move on
            if comment is None:
                break

            # Clear out the comment syntax
            if comment.startswith("//"):
                comment = comment.replace("//", "", 1)
            elif comment.startswith("/*"):
                comment = comment.replace("/*", "", 1)
                comment = comment[::-1].replace("/*", "", 1)[::-1]

            comment = comment.strip()

            # Split any multi-line comments
            components = [c.strip() for c in comment.split("\n")]
            comments.extend(components)

            # Pull out any whitespace
            _ = scanner.scan(Patterns.whitespace)

        # Get the entry line. Always try with quotes first to avoid matching
        # the "quoteless" style and then including the quotes in the key.
        entry = scanner.scan(Patterns.entry)
        regular_entry = True

        if entry is None:
            entry = scanner.scan(Patterns.quoteless_key_entry)
            regular_entry = False

            if entry is None:
                if scanner.has_more():
                    raise DotStringsException(
                        f"Expected an entry at offset {scanner.offset}"
                    )
                break

        # Now extract the key and value
        if regular_entry:
            entry_matches = Patterns.entry.search(entry)
        else:
            entry_matches = Patterns.quoteless_key_entry.search(entry)

        if not entry_matches:
            raise DotStringsException(
                f"Failed to parse entry at offset {scanner.offset}"
            )

        key = entry_matches.group(1)
        value = entry_matches.group(2)

        strings.append(DotStringsEntry(key, value, comments, scanner.line))

    return strings


def load_dict(file_details: BinaryIO | str) -> list[DotStringsDictEntry]:
    """Parse the contents of a .stringsdict file from a file pointer.

    :param file_details: The file pointer or a file path

    :returns: A list of `DotStringEntry`s
    """

    # If it's a file pointer, read in the contents and parse
    if not isinstance(file_details, str):
        contents = file_details.read()
        return loads_dict(contents)

    with open(file_details, "rb") as stringsdict_file:
        return load_dict(stringsdict_file)


def loads_dict(contents: bytes) -> list[DotStringsDictEntry]:
    """Parse the contents of a .stringsdict file from binary data.

    :param contents: The binary data of a .stringsdict file

    :returns: A list of `DotStringEntry`s
    """

    strings_dict = plistlib.loads(contents)

    if not isinstance(strings_dict, dict):
        raise DotStringsException("stringsdict format is incorrect")

    entries = []
    for key, entry in strings_dict.items():
        if not isinstance(entry, dict):
            raise DotStringsException("stringsdict entry format is incorrect")

        entries.append(DotStringsDictEntry.parse(key, entry))

    return entries
