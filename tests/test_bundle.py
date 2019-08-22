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
        self.bundle_path = os.path.abspath(os.path.join(current_folder_path, "string_bundle"))

    def test_load_all(self):
        """Test that an entire bundle loads."""
        strings = dotstrings.load_all_strings(self.bundle_path)
        self.assertEqual(["en", "fr"], sorted(list(strings.keys())))

        english_strings = strings["en"]
        self.assertEqual(["One", "Two"], sorted(list(english_strings.keys())))

        french_strings = strings["fr"]
        self.assertEqual(["One", "Two"], sorted(list(french_strings.keys())))
