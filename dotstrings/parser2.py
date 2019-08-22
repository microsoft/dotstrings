#!/usr/bin/env python3

"""Utilities for dealing with .strings files"""

from typing import List, Optional, TextIO, Union

import ply.lex as lex

from dotstrings.string_types import DotStringsEntry



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
        encoding_list = ["utf-8", "utf-16-le"]

    for encoding_option in encoding_list:
        try:
            with open(file_details, "r", encoding=encoding_option) as strings_file:
                return load(strings_file, encoding=encoding_option)
        except UnicodeDecodeError:
            # We should log this or something?
            pass

    raise Exception("Could not determine encoding for file at path: {file_details}")


def _generate_lexer():

    # TODO: This needs to handle non-quoted keys too

    tokens = (
        'COMMENT',
        'STRING',
        'EQUALS',
        'SEMI_COLON'
    )

    t_EQUALS = r'='
    t_SEMI_COLON = r';'

    def t_STRING(t):
        r'"([^"\n]|(\\"))*"'
        t.value = t.value[1:-1]
        return t

    def t_COMMENT(t):
        r'/\*(.|\n)*?\*/'
        t.lineno += t.value.count('\n')
        t.value = t.value.lstrip("/*")
        t.value = t.value.rstrip("/*")
        t.value = t.value.strip()
        return t

    t_ignore = ' \t'

    def t_newline(t):
        r'\n+'
        t.lexer.lineno += len(t.value)

    def t_error(t):
        print("Illegal character '%s'" % t.value[0])
        t.lexer.skip(1)


    return lex.lex()



def _generate_tokens(lexer: lex.Lexer) -> List[lex.LexToken]:
    all_tokens = []

    while True:
        token = lexer.token()
        if not token:
            break
        all_tokens.append(token)

    return all_tokens


def _generate_groups(all_tokens: List[lex.LexToken]) -> List[List[lex.LexToken]]:
    groups = []
    current_group = []
    for token in all_tokens:
        current_group.append(token)
        if token.type == "SEMI_COLON":
            groups.append(current_group)
            current_group = []
            continue

    if len(current_group) != 0:
        raise Exception(f"Entry was not terminated on line {current_group[-1].lineno}")

    return groups


def loads(string: str) -> List[DotStringsEntry]:
    """Parse the contents of a .strings file.

    :param string: The contents of a .strings file

    :returns: A list of `DotStringsEntry`s"""

    lexer = _generate_lexer()

    lexer.input(string)

    all_tokens = _generate_tokens(lexer)
    groups = _generate_groups(all_tokens)

    entries = []

    for group in groups:
        comment_entries = []
        while True:
            token = group[0]
            if token.type != "COMMENT":
                break
            comment_entries.append(token.value)
            group.pop(0)

        comment = "\n".join(comment_entries)

        token = group.pop(0)

        if token.type != "STRING":
            raise Exception(f"Expected a string at position {token.lineno}:{token.lexpos}")

        key = token.value

        token = group.pop(0)

        if token.type != "EQUALS":
            raise Exception(f"Expected '=' at position {token.lineno}:{token.lexpos}")

        token = group.pop(0)

        if token.type != "STRING":
            raise Exception(f"Expected a string at position {token.lineno}:{token.lexpos}")

        value = token.value

        token = group.pop(0)

        if token.type != "SEMI_COLON":
            raise Exception(f"Expected ';' at position {token.lineno}:{token.lexpos}")

        entries.append(DotStringsEntry(key, value, comment if len(comment) else None))

    return entries
