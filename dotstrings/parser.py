#!/usr/bin/env python3

"""Utilities for dealing with .strings files"""

import re
from typing import List, Match, Optional, TextIO, Tuple, Union

from dotstrings.dot_strings_entry import DotStringsEntry


_ENTRY_REGEX = r'^"(.+)"\s?=\s?"(.*)";$'
_ENTRY_PATTERN = re.compile(_ENTRY_REGEX)

_NS_ENTRY_REGEX = r'^(NS[^ ]+)\s?=\s?"(.*)";$'
_NS_ENTRY_PATTERN = re.compile(_NS_ENTRY_REGEX)


def load(file_details: Union[TextIO, str], encoding: Optional[str] = None) -> List[DotStringsEntry]:
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
        encoding_list = ["utf-8", "utf-16-le", "utf-16-be"]

    for encoding_option in encoding_list:
        try:
            with open(file_details, "r", encoding=encoding_option) as strings_file:
                return load(strings_file)
        except UnicodeDecodeError:
            pass

    raise Exception(f"Could not determine encoding for file at path: {file_details}")


def loads(contents: str) -> List[DotStringsEntry]:
    """Parse the contents of a .strings file.

    Note: CRLF is not supported in strings.

    :param contents: The contents of a .strings file

    :returns: A list of `DotStringsEntry`s"""

    # Sometimes we have CRLF. It's easier to just replace now. This could, in
    # theory, cause issues, but we just don't support it for now.
    if "\r\n" in contents:
        raise Exception("Strings contain CRLF")
    contents = contents.replace("\r\n", "\n")

    # Let's split so that we have a single item and it's comments together
    entries = contents.split('";')

    # Remove any empty entries
    entries = [entry for entry in entries if len(entry.strip()) > 0]

    # Add the splitter back on the end
    entries = [entry + '";' for entry in entries]

    parsed_entries: List[DotStringsEntry] = []

    # Now we can work on parsing them one by one
    for entry in entries:
        parsed_entries.append(_parse_entry(entry))

    return parsed_entries


def _find_entry(entry_lines: List[str]) -> Tuple[int, Optional[Match]]:
    """Search for the entry in some entry lines

    :param entry_lines: The lines for an entry from a .strings file (including comments)

    :returns: A tuple with the index of the match and the match itself
    """

    for index, line in enumerate(entry_lines):

        # Naive checks to avoid doing a regex if we don't have to
        if len(line) == 0:
            continue

        if len(line.strip()) == 0:
            continue

        if line.startswith(" "):
            continue

        match = _ENTRY_PATTERN.match(line)
        if match:
            return index, match

        # We didn't match so try the NS entry one
        match = _NS_ENTRY_PATTERN.match(line)
        if match:
            return index, match

    return 0, None


def _parse_entry(entry: str) -> DotStringsEntry:
    """Parse a single entry in a .strings file and its comments.

    :param entry: A single entry from a .strings file

    :returns: A parsed entry value

    :raises Exception: If we fail to parse the entry
    """

    # pylint: disable=too-many-branches

    lines = entry.split("\n")

    entry_index, entry_match = _find_entry(lines)

    # If we didn't find it, then that's a problem
    if entry_match is None:
        raise Exception("Failed to find key and value in entry:\n" + entry)

    # We also expect it to be the last line, so if it's not, then that's a problem too
    if entry_index != len(lines) - 1:
        raise Exception("Found key and value in an unexpected position in entry:\n" + entry)

    # We now have the key and value
    key = entry_match.group(1)
    value = entry_match.group(2)

    # Just the comment to go

    # We already know the key and value were on the last line, so let's drop it
    lines = lines[:-1]

    comment = ""
    in_comment = False

    for line in lines:

        if not in_comment and "/*" in line:
            in_comment = True

        if not in_comment:
            continue

        if line.strip().startswith("/*"):
            line = line.replace("/*", "")

        if line.strip().endswith("*/"):
            line = line.replace("*/", "")

        comment += line.strip() + "\n"

        if "*/" in line:
            in_comment = False

    # If we didn't find any comment, set it to None
    if len(comment) == 0:
        return DotStringsEntry(key, value, [])

    comments = comment.split("\n")
    comments = [comment.strip() for comment in comments]
    comments = [comment for comment in comments if len(comment) > 0]

    return DotStringsEntry(key, value, comments)

    # pylint: enable=too-many-branches
