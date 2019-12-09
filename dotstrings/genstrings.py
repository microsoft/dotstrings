"""Wrapper around the genstrings command"""

import os
import shutil
import subprocess
import tempfile
from typing import List


def _convert_to_utf8(file_path: str) -> None:
    """Take a UTF-16 file and convert to UTF-8.

    NOTE: This will replace the existing file

    :param file_path: The path of the file to convert

    :raises Exception: If we are unable to convert
    """

    temp_file_path = tempfile.mktemp()

    iconv_command = f'iconv -f UTF-16 -t UTF-8 "{file_path}" > "{temp_file_path}"'

    if subprocess.run(iconv_command, shell=True).returncode != 0:
        raise Exception("Unable to convert from UTF-16 to UTF-8!")

    shutil.move(temp_file_path, file_path)


def generate_strings(
    *, output_directory: str, file_paths: List[str], clear_existing: bool = True
) -> None:
    """Run the genstrings command over the files passed in.

    Genstrings scans code files for usage of the `NSLocalizedString` macro. It
    the generates the corresponding .strings file from these. e.g. If you have:

    ```objc
    label.text = NSLocalizedString(@"Hello World", @"Greeting to the user");
    ```

    then the tool will find this and generate an `en.lproj/Localizable.strings`
    file with the content:

    ```
    /* Greeting to the user */
    "Hello World" = "Hello World";
    ```

    However, if you specify a table in your `NSLocalizedString` call, then
    instead of using the default `Localizable.strings` file, it will generate
    `MyTable.strings`.

    :param str output_directory: The location to place the output files (this
                                 folder will contain an en.lproj folder after)
    :param List[str] file_paths: The paths to the files that should be scanned
    :param bool clear_existing: Set to True when the existing files in the
                                output directory should be wiped before
                                generating the new strings. Defaults to True.

    :raises Exception: If we can't generate the .strings files
    """

    # Determine output paths
    english_strings_directory = os.path.join(output_directory, "en.lproj")

    # Create output directory
    os.makedirs(english_strings_directory, exist_ok=True)

    # Empty existing strings
    if clear_existing:
        for table in os.listdir(english_strings_directory):
            with open(os.path.join(english_strings_directory, table), "w") as table_file:
                table_file.write("")

    # We can't pass in too many files on the command line or the argument list
    # is too long. To avoid this, we do it in chunks of 100.
    files_per_iteration = 100

    for i in range(0, (len(file_paths) // files_per_iteration) + 1):

        # Take the next group of files
        current_files = file_paths[i * files_per_iteration : (i + 1) * files_per_iteration]

        genstrings_command = ["xcrun", "extractLocStrings", "-a", "-noPositionalParameters", "-u"]
        genstrings_command += ["-o", english_strings_directory]
        genstrings_command.extend(current_files)

        try:
            output = subprocess.run(
                genstrings_command,
                universal_newlines=True,
                check=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ).stdout

            output = output.strip()

            if len(output) > 0:
                raise Exception(f"Encountered an error generating strings: {output}")
        except subprocess.CalledProcessError as ex:
            raise Exception(f"Unable generate .strings files! {ex}")

    # Convert all .strings files to UTF-8
    for file_name in os.listdir(english_strings_directory):
        file_path = os.path.join(english_strings_directory, file_name)
        # Check for file type and .strings extension
        if file_name.endswith(".strings") and os.path.isfile(file_path):
            _convert_to_utf8(file_path)
