"""Simple tests."""

# pylint: disable=line-too-long

import filecmp
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.abspath(os.path.join(os.path.abspath(__file__), "..", "..")))
import dotstrings


class NormalizationTests(unittest.TestCase):
    """Normalization tests."""

    def setUp(self):
        current_file_path = os.path.abspath(__file__)
        current_folder_path = os.path.dirname(current_file_path)
        self.strings_path = os.path.abspath(os.path.join(current_folder_path, "strings_files"))

    def test_normalization(self):
        """Test normalizing a strings file works."""
        random_string_path = os.path.join(self.strings_path, "randomized.strings")
        normalized_string_path = os.path.join(self.strings_path, "randomized_normalized.strings")
        output_file = tempfile.mktemp(suffix=".strings")
        dotstrings.normalize(random_string_path, output_file)
        self.assertTrue(filecmp.cmp(normalized_string_path, output_file), "Files were not the same")
        os.remove(output_file)
