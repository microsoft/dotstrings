"""Utilities for dealing with .strings files"""

import os
from typing import Dict, List, Optional, Set

from dotstrings.parser import load, loads, load_dict, loads_dict
from dotstrings.dot_strings_entry import DotStringsEntry
from dotstrings.dot_stringsdict_entry import DotStringsDictEntry, Variable
from dotstrings.localized_bundle import LocalizedBundle
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


def stringsdict_file_path(stringsdict_folder: str, language: str, table_name: str) -> str:
    """Generate the .stringsdict file path from the details supplied.

    :param stringsdict_folder: The location of the strings folder (which contains
                               all the *.lproj folders)
    :param language: The language code for the file
    :param table_name: The name of the table (file name)

    :returns: The path to the strings file
    """
    return os.path.join(
        language_folder_path(stringsdict_folder, language), f"{table_name}.stringsdict"
    )


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
        if not table.endswith(".strings"):
            continue
        table_name = table.replace(".strings", "")
        results[table_name] = load_table(strings_folder, language, table_name)

    return results


def load_all_strings(strings_folder: str) -> LocalizedBundle:
    """Load the .strings tables for a given language

    :param strings_folder: The location of the strings folder (which contains
                           all the *.lproj folders)
    :param language: The language code to load

    :returns: A LocalizedBundle containing the results
    """

    languages = languages_in_folder(strings_folder)

    results = {}

    for language in sorted(languages):
        results[language] = load_language_tables(strings_folder, language)

    return LocalizedBundle(results)


def normalize(
    strings_path: str,
    output_path: Optional[str] = None,
    remove_duplicates: bool = True,
    sort_comments: bool = True,
) -> None:
    """Load in the specified .strings table, normalize it, and write it back out.

    Normalizing consists of sorting by key, then comments, and (usually)
    deduplicating before writing back out.

    :param strings_path: The location of the strings file
    :param output_path: The location to write the sorted file to. If None, it
                        will overwrite the input file.
    :param remove_duplicates: By default, any duplicates will be removed and
                              their comments combined. Set to False to raise
                              an exception instead
    :param sort_comments: By default comments will be sorted in alphabetical
                          order. However, if you use linebreaks in your comments
                          you will wish to turn this off. It also removes
                          duplicates.
    """

    entries = load(strings_path)
    entries.sort(key=lambda x: [x.key] + x.comments)

    deduped_entries = [entries[0]]

    for entry in entries[1:]:

        # If the keys are different, just add to the list and move on
        if deduped_entries[-1].key != entry.key:
            deduped_entries.append(entry)
            continue

        # If we have duplicate keys but the values don't match, that's an
        # exception, whether or not we are removing duplicates
        if deduped_entries[-1].value != entry.value or not remove_duplicates:
            raise Exception(f"Found duplicate strings with key: {entry.key}")

        deduped_entries[-1].comments.extend(entry.comments)

    if sort_comments:
        for entry in deduped_entries:
            entry.comments = list(set(entry.comments))
            entry.comments.sort()

    if output_path is None:
        output_path = strings_path

    with open(output_path, "w", encoding="utf-8") as strings_file:
        for entry in deduped_entries:
            strings_file.write(entry.strings_format())
            strings_file.write("\n\n")
