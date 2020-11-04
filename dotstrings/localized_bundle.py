"""Representation of a localized bundle."""

from typing import cast, Dict, List, Set

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

            # Build up a map of languages to table names

            found_tables: Dict[str, Set[str]] = {}
            for language, table_map in self.raw_entries.items():
                # table_map is a dictionary of names to lists of strings
                found_tables[language] = set(table_map.keys())

            if len(found_tables) == 0:
                return []

            base_language = list(found_tables.keys())[0]
            base_language_tables = found_tables[base_language]

            for language, table_names in found_tables.items():
                extra_tables = table_names - base_language_tables
                missing_tables = base_language_tables - table_names

                if len(extra_tables) > 0:
                    raise Exception(
                        f"The following table names were in {language}"
                        + f" but not in {base_language}: {extra_tables}"
                    )

                if len(missing_tables) > 0:
                    raise Exception(
                        f"The following table names were in {base_language}"
                        + f" but not in {language}: {missing_tables}"
                    )

            return list(base_language_tables)

        all_table_names = set()

        for table_map in self.raw_entries.values():
            for table in table_map.keys():
                all_table_names.add(table)

        return list(all_table_names)

    def tables_for_language(self, language: str) -> Dict[str, List[LocalizedString]]:
        """Return the tables for a language.

        :param language: The language to get the tables for

        :returns: A dictionary of table names to lists of strings
        """
        sentinel = object()
        result = self.raw_entries.get(language, sentinel)

        if result is sentinel:
            raise Exception(f"There were no entries for language: {language}")

        return cast(Dict[str, List[LocalizedString]], result)

    def table_for_languages(
        self, table: str, *, allow_missing: bool = False
    ) -> Dict[str, List[LocalizedString]]:
        """Return a dictionary of languages to strings for a given table.

        :param table: The table to load the data for
        :param bool allow_missing: Set to True to allow a table to be missing for any languages

        :returns: A dictionary of language codes to a list of strings
        """
        results = {}

        for language, table_map in self.raw_entries.items():
            sentinel = object()
            table_data = table_map.get(table, sentinel)

            if table_data is sentinel and language == "Base":
                continue

            if table_data is sentinel and not allow_missing:
                raise Exception(f"Could not find table {table} for language {language}")

            results[language] = cast(List[LocalizedString], table_data)

        return results

    def tables(
        self, *, validate_missing: bool = True
    ) -> Dict[str, Dict[str, List[LocalizedString]]]:
        """Return the entries in the bundle, first keyed by table, then by language.

        :param bool validate_missing: Set to False to disable the check that a table exists for every language

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
            results[table_name] = self.table_for_languages(
                table_name, allow_missing=(not validate_missing)
            )

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
