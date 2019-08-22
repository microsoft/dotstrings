"""Utilities for dealing with .strings files"""

import os
from typing import Dict, List, Set

from dotstrings.parser import load, loads
from dotstrings.dot_strings_entry import DotStringsEntry
from dotstrings.localized_string import LocalizedString


def language_folder_path(strings_folder: str, language: str) -> str:
    """Generate the folder path for a language.

    :param strings_folder: The location of the strings folder (which contains
                           all the *.lproj folders)
    :param language: The language code for the file

    :returns: The path to the strings file
    """
    return os.path.join(strings_folder, f"{language}.lproj")


def strings_file_path(strings_folder: str, language: str, table_name: str) -> str:
    """Generate the .strings file path from the details supplied.

    :param strings_folder: The location of the strings folder (which contains
                           all the *.lproj folders)
    :param language: The language code for the file
    :param table_name: The name of the table (file name)

    :returns: The path to the strings file
    """
    return os.path.join(language_folder_path(strings_folder, language), f"{table_name}.strings")


def languages_in_folder(strings_folder: str) -> Set[str]:
    """Find all the languages in a folder

    This looks for *.lproj folders.

    :param strings_folder: The location of the strings folder (which contains
                           all the *.lproj folders)

    :returns: A set containing all the languages.
    """
    languages = os.listdir(strings_folder)
    languages = [language for language in languages if language.endswith(".lproj")]
    return {language.replace(".lproj", "") for language in languages}


def load_table(strings_folder: str, language: str, table_name: str) -> List[LocalizedString]:
    """Load the specified .strings table

    :param strings_folder: The location of the strings folder (which contains
                           all the *.lproj folders)
    :param language: The language code to load
    :param table_name: The name of the table to load

    :returns: A list of strings in the table
    """

    table_path = strings_file_path(strings_folder, language, table_name)
    strings = load(table_path)
    return LocalizedString.from_dotstring_entries(
        entries=strings, language=language, table=table_name
    )


def load_language_tables(strings_folder: str, language: str) -> Dict[str, List[LocalizedString]]:
    """Load the .strings tables for a given language

    :param strings_folder: The location of the strings folder (which contains
                           all the *.lproj folders)
    :param language: The language code to load

    :returns: A dictionary of results. The key is the table, the value is the
              list of strings in the table
    """

    language_folder = language_folder_path(strings_folder, language)

    results = {}

    for table in os.listdir(language_folder):
        table_name = table.replace(".strings", "")
        results[table_name] = load_table(strings_folder, language, table_name)

    return results


def load_all_strings(strings_folder: str) -> Dict[str, Dict[str, List[LocalizedString]]]:
    """Load the .strings tables for a given language

    :param strings_folder: The location of the strings folder (which contains
                           all the *.lproj folders)
    :param language: The language code to load

    :returns: A dictionary of results. The key is the language, the value is a
              dictionary of language results (key is the table, value is the
              list of string entries)
    """

    languages = languages_in_folder(strings_folder)

    results = {}

    for language in languages:
        results[language] = load_language_tables(strings_folder, language)

    return results
