"""Simple tests."""

# pylint: disable=line-too-long

import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import dotstrings


class SimpleTests(unittest.TestCase):
    """Simple tests."""

    def setUp(self):
        current_file_path = os.path.abspath(__file__)
        current_folder_path = os.path.dirname(current_file_path)
        self.strings_path = os.path.abspath(os.path.join(current_folder_path, "strings_files"))

    def test_single_string(self):
        """Test that a single string load works."""
        single_string_path = os.path.join(self.strings_path, "single_string.strings")
        entries = dotstrings.load(single_string_path)
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry.key, "This is a key")
        self.assertEqual(entry.value, "This is a value")
        self.assertEqual(0, len(entry.comments))

    def test_single_string_with_comment(self):
        """Test that a single string with comment load works."""
        single_string_path = os.path.join(self.strings_path, "single_string_with_comment.strings")
        entries = dotstrings.load(single_string_path)
        self.assertEqual(len(entries), 1)
        entry = entries[0]
        self.assertEqual(entry.key, "This is a key")
        self.assertEqual(entry.value, "This is a value")
        self.assertEqual(entry.comments, ["This is a comment.", "It spans multiple lines"])

    def test_multi_string_with_comment(self):
        """Test that multiple strings with comments load works."""
        multi_string_path = os.path.join(self.strings_path, "multi_string_with_comment.strings")
        entries = dotstrings.load(multi_string_path)
        self.assertEqual(len(entries), 4)

        self.assertEqual(entries[0].key, "One")
        self.assertEqual(entries[0].value, "1")
        self.assertEqual(entries[0].comments, ["More comment", "Multi-line", "comment"])

        self.assertEqual(entries[1].key, "Two")
        self.assertEqual(entries[1].value, "2")
        self.assertEqual(entries[1].comments, ["Single line comment"])

        self.assertEqual(entries[2].key, "Three")
        self.assertEqual(entries[2].value, "3")
        self.assertEqual(entries[2].comments, ["Three Comment"])

        self.assertEqual(entries[3].key, "Four")
        self.assertEqual(entries[3].value, "4")
        self.assertEqual(entries[3].comments, ["No line break comment"])
