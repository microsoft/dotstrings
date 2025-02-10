"""Simple tests."""

# pylint: disable=line-too-long

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import dotstrings


class BundleTests(unittest.TestCase):
    """Bundle tests."""

    def setUp(self):
        current_file_path = os.path.abspath(__file__)
        current_folder_path = os.path.dirname(current_file_path)
        self.bundle_path = os.path.abspath(
            os.path.join(current_folder_path, "string_bundle")
        )
        self.bundle2_path = os.path.abspath(
            os.path.join(current_folder_path, "string_bundle2")
        )
        self.quoteless_path = os.path.abspath(
            os.path.join(current_folder_path, "quoteless_bundle")
        )

    def test_load_all(self):
        """Test that an entire bundle loads."""
        strings = dotstrings.load_all_strings(self.bundle_path).raw_entries
        self.assertEqual(["en", "fr"], sorted(list(strings.keys())))

        english_strings = strings["en"]
        self.assertEqual(["One", "Two"], sorted(list(english_strings.keys())))

        french_strings = strings["fr"]
        self.assertEqual(["One", "Two"], sorted(list(french_strings.keys())))

    def test_load_quoteless(self):
        """Test that the quoteless key bundle loads."""
        strings = dotstrings.load_all_strings(self.quoteless_path).raw_entries
        self.assertEqual(["en", "fr"], sorted(list(strings.keys())))

        english_strings = strings["en"]["QuotelessKeys"]
        self.assertEqual(
            [
                "NSLocationAlwaysAndWhenInUseUsageDescription",
                "NSPhotoLibraryUsageDescription",
            ],
            sorted([string.key for string in english_strings]),
        )

        french_strings = strings["fr"]["QuotelessKeys"]
        self.assertEqual(
            [
                "NSLocationAlwaysAndWhenInUseUsageDescription",
                "NSPhotoLibraryUsageDescription",
            ],
            sorted([string.key for string in french_strings]),
        )

    def test_localized_bundle_languages(self):
        """Test that the languages call in localized bundles works."""
        strings = dotstrings.load_all_strings(self.bundle_path)
        self.assertEqual(sorted(strings.languages()), ["en", "fr"])

    def test_localized_bundle_table_names(self):
        """Test that the table_names call in localized bundles works."""
        strings = dotstrings.load_all_strings(self.bundle_path)
        self.assertEqual(sorted(strings.table_names(validate_identical=True)), ["One", "Two"])
        self.assertEqual(sorted(strings.table_names(validate_identical=False)), ["One", "Two"])

    def test_localized_bundle_tables(self):
        """Test that the tables call in localized bundles works."""
        strings = dotstrings.load_all_strings(self.bundle_path)
        tables = strings.tables()
        self.assertEqual(sorted(list(tables.keys())), ["One", "Two"])

        table_one = tables["One"]
        self.assertEqual(sorted(list(table_one.keys())), ["en", "fr"])
        self.assertEqual(len(table_one["en"]), 2)
        self.assertEqual(len(table_one["fr"]), 2)

        table_two = tables["Two"]
        self.assertEqual(sorted(list(table_two.keys())), ["en", "fr"])
        self.assertEqual(len(table_two["en"]), 1)
        self.assertEqual(len(table_two["fr"]), 1)

    def test_localized_bundle_tables_for_language(self):
        """Test that the tables_for_language call in localized bundles works."""
        strings = dotstrings.load_all_strings(self.bundle_path)
        self.assertEqual(sorted(strings.tables_for_language("en")), ["One", "Two"])
        self.assertEqual(sorted(strings.tables_for_language("fr")), ["One", "Two"])

    def test_localized_bundle_table_for_languages(self):
        """Test that the table_for_languages call in localized bundles works."""
        strings = dotstrings.load_all_strings(self.bundle_path)

        one_languages = strings.table_for_languages("One")
        self.assertEqual(sorted(list(one_languages.keys())), ["en", "fr"])

        one_english = one_languages["en"]
        self.assertEqual(len(one_english), 2)

        one_french = one_languages["fr"]
        self.assertEqual(len(one_french), 2)

        two_languages = strings.table_for_languages("Two")
        self.assertEqual(sorted(list(two_languages.keys())), ["en", "fr"])

        two_english = two_languages["en"]
        self.assertEqual(len(two_english), 1)

        two_french = two_languages["fr"]
        self.assertEqual(len(two_french), 1)

    def test_localized_bundle_merge(self):
        """Test that the merge call in localized bundles works."""
        bundle = dotstrings.load_all_strings(self.bundle_path)
        bundle2 = dotstrings.load_all_strings(self.bundle2_path)

        bundle.merge_bundle(bundle2)

        self.assertEqual(["en", "fr"], sorted(list(bundle.raw_entries.keys())))

        english_strings = bundle.raw_entries["en"]
        self.assertEqual(sorted(["One", "Two", "Three"]), sorted(list(english_strings.keys())))

        french_strings = bundle.raw_entries["fr"]
        self.assertEqual(sorted(["One", "Two", "Three"]), sorted(list(french_strings.keys())))
