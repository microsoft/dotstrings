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
        single_string_path = os.path.join(self.strings_path, "multi_string_with_comment.strings")
        entries = dotstrings.parser2.load(single_string_path)
        print(entries)