"""Simple tests."""

# pylint: disable=line-too-long

import dotstrings
import os
import sys
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))


class SimpleTests(unittest.TestCase):
    """Simple tests."""

    def setUp(self):
        current_file_path = os.path.abspath(__file__)
        current_folder_path = os.path.dirname(current_file_path)
        self.strings_path = os.path.abspath(os.path.join(current_folder_path, "strings_files"))
        self.stringsdict_path = os.path.abspath(os.path.join(current_folder_path, "stringsdict_files"))

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

    def test_stringsdict(self):
        """Test that stringsdict load works."""
        stringsdict_file_path = os.path.join(self.stringsdict_path, "example.stringsdict")
        entries = dotstrings.load_dict(stringsdict_file_path)
        self.assertEqual(len(entries), 2)

        self.assertEqual(entries[0].key, "i_have_cats_and_dogs")
        self.assertEqual(entries[0].value, "I have %#@catCount@ and %#@dogCount@")
        self.assertEqual(len(entries[0].variables), 2)

        variables = entries[0].variables
        cat_variable = variables.get("catCount")
        self.assertIsNotNone(cat_variable)

        self.assertEqual(cat_variable.value_type, "d")
        self.assertEqual(cat_variable.zero_value, "no cat")
        self.assertEqual(cat_variable.one_value, "a cat")
        self.assertEqual(cat_variable.other_value, "%d cats")

    def test_strings_format(self):
        """Test that .strings formatting works."""
        strings_file_path = os.path.join(self.strings_path, "randomized.strings")
        entries = dotstrings.load(strings_file_path)

        self.assertEqual(entries[0].strings_format(), '/* This is a\n   multiline comment */\n"carry" = "breathe";')
        self.assertEqual(entries[1].strings_format(
        ), '/* This is another\n   multiline comment, but for a dupe */\n"condition" = "outgoing";')
        self.assertEqual(entries[2].strings_format(), '/* precious */\n"condition" = "outgoing";')

    def test_string_with_uneven_whitespace(self):
        """Test that string with uneven whitespaces work"""
        string_with_uneven_whitespace_path = os.path.join(self.strings_path, "string_with_uneven_whitespace.strings")
        entries = dotstrings.load(string_with_uneven_whitespace_path)
        self.assertEqual(len(entries), 3)

        self.assertEqual(entries[0].key, "This is a key")
        self.assertEqual(entries[0].value, "This is a value")

        self.assertEqual(entries[1].key, "This is also a key")
        self.assertEqual(entries[1].value, "This is also a value")

        self.assertEqual(entries[2].key, "This is again a key")
        self.assertEqual(entries[2].value, "This is again a value")

    def test_string_with_multiline_value(self) -> None:
        """Test the strings that have values spanning multiple lines"""

        multiline_value_path = os.path.join(self.strings_path, "string_with_multiline_value.strings")
        entries = dotstrings.load(multiline_value_path)
        self.assertEqual(len(entries), 3)

        self.assertEqual(entries[0].key, "key-case1")
        self.assertEqual(entries[0].value, """value
that
has
newlines""")
        self.assertEqual(entries[0].value, "value\nthat\nhas\nnewlines")

        self.assertEqual(entries[1].key, "key-case2")
        self.assertEqual(entries[1].value, """Major text in one line and just the closing in next line
""")
        self.assertEqual(entries[1].value, "Major text in one line and just the closing in next line\n")

        self.assertEqual(entries[2].key, "key-case3")
        self.assertEqual(entries[2].value, """A paragraph like text structure

that goes like this and goes on and on

and ends here""")

        self.assertEqual(
            entries[2].value, "A paragraph like text structure\n\nthat goes like this and goes on and on\n\nand ends here")
