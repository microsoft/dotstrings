"""Representation of a localized bundle."""

from typing import Dict, List

from dotstrings.localized_string import LocalizedString


class LocalizedBundle:
    """Representation of a localized bundle.

    :param raw_entries: The raw dictionary entries that were parsed from disk
    """

    def __init__(self, raw_entries: Dict[str, Dict[str, List[LocalizedString]]]) -> None:
        self.raw_entries = raw_entries

    def languages(self) -> List[str]:
        """Return the languages supported in the bundle

        :returns: A list of language codes
        """
        return list(self.raw_entries.keys())

    def table_names(self, validate_identical: bool = False) -> List[str]:
        """Return the tables in the bundle.

        :param validate_identical: Set to True to confirm all languages have the
                                   same tables in them

        :returns: A list of table names
        """

        if validate_identical:

            found_keys = []
            for table_map in self.raw_entries.values():
                found_keys.append(sorted(table_map.keys()))

            pairs = zip(found_keys, found_keys[1:] + found_keys[:1])

            for first, second in pairs:
                if first != second:
                    raise Exception("Not all languages have the same tables")

            return found_keys[0]

        found_tables = set()

        for table_map in self.raw_entries.values():
            for table in table_map.keys():
                found_tables.add(table)

        return list(found_tables)

    def tables_for_language(self, language: str) -> Dict[str, List[LocalizedString]]:
        """Return the tables for a language.

        :param language: The language to get the tables for

        :returns: A dictionary of table names to lists of strings
        """
        return self.raw_entries[language]

    def table_for_languages(self, table: str) -> Dict[str, List[LocalizedString]]:
        """Return a dictionary of languages to strings for a given table.

        :param table: The table to load the data for

        :returns: A dictionary of language codes to a list of strings
        """
        results = {}

        for language, table_map in self.raw_entries.items():
            results[language] = table_map[table]

        return results

    def tables(self) -> Dict[str, Dict[str, List[LocalizedString]]]:
        """Return the entries in the bundle, first keyed by table, then by language.

        Example response:

        ```
        {
            "MyTable": {
                "en": [x, y, z],
                "fr": [x, y, z]
            },
            "OtherTable": {
                "en": [a, b, c],
                "fr": [a, b, c]
            }
        }
        ```

        :returns: A dictionary of table names to a dictionary of languages to strings
        """
        results = {}

        for table_name in self.table_names():
            results[table_name] = self.table_for_languages(table_name)

        return results

    def merge_bundle(self, other: "LocalizedBundle") -> None:
        """Merge another bundle into this one.

        Any identical tables results in an exception

        :param other: The other bundle to merge into this one

        :raises Exception: If the other bundle has identical tables
        """

        for language, table_map in other.raw_entries.items():
            for table, strings in table_map.items():
                if self.raw_entries.get(language) is None:
                    self.raw_entries[language] = {}
                self.raw_entries[language][table] = strings
