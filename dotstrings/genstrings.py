"""Wrapper around the genstrings command"""

import os
import shutil
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor, as_completed

from dotstrings.exceptions import DotStringsException


def _convert_to_utf8(file_path: str) -> None:
    """Take a UTF-16 file and convert to UTF-8.

    NOTE: This will replace the existing file

    :param file_path: The path of the file to convert

    :raises Exception: If we are unable to convert
    """

    temp_file_path = tempfile.mktemp()

    iconv_command = f'iconv -f UTF-16 -t UTF-8 "{file_path}" > "{temp_file_path}"'

    if subprocess.run(iconv_command, shell=True, check=False).returncode != 0:
        raise DotStringsException("Unable to convert from UTF-16 to UTF-8!")

    shutil.move(temp_file_path, file_path)


def _extract_strings(file_paths: list[str], english_strings_directory: str) -> str | None:
    """Extract strings for a chunk of files.

    :param list[str] file_paths: The files to extract strings from
    :param str english_strings_directory: The directory to place the extracted strings

    :return: An error message if extraction fails, otherwise None
    """
    genstrings_command = ["xcrun", "extractLocStrings", "-a", "-noPositionalParameters", "-u"]
    genstrings_command += ["-o", english_strings_directory]
    genstrings_command.extend(file_paths)

    try:
        output_bytes = subprocess.run(
            genstrings_command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ).stdout

        # We decode here rather than in the subprocess call because it seems
        # that extractLocStrings can occasionally flush its buffer without
        # writing the entirety of a character out. When that happens, the
        # text wrapper tries to decode it and fails. By buffering all bytes
        # until the end of the command and then decoding, we avoid this
        # issue.
        output = output_bytes.decode("utf-8", errors="backslashreplace")

        output = output.strip()

        if len(output) > 0:
            return f"Encountered an error generating strings: {output}"
        return None
    except subprocess.CalledProcessError as ex:
        return f"Unable generate .strings files! {ex}"


def generate_strings(
    *,
    output_directory: str,
    file_paths: list[str],
    clear_existing: bool = True,
    max_workers: int = 1,
) -> None:
    """Run the genstrings command over the files passed in.

    Genstrings scans code files for usage of the `NSLocalizedString` macro. It
    then generates the corresponding .strings file from these. e.g. If you have:

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
    :param list[str] file_paths: The paths to the files that should be scanned
    :param bool clear_existing: Set to True when the existing files in the
                                output directory should be wiped before
                                generating the new strings. Defaults to True.
    :param int max_workers: The maximum number of worker threads to use for parallel processing.
                            Defaults to 1 (no parallelism).

    :raises Exception: If we can't generate the .strings files
    """

    # Determine output paths
    english_strings_directory = os.path.join(output_directory, "en.lproj")

    # Create output directory
    os.makedirs(english_strings_directory, exist_ok=True)

    # Empty existing strings
    if clear_existing:
        for table in os.listdir(english_strings_directory):
            # Do not clear non .strings files
            if not table.endswith(".strings"):
                continue
            with open(
                os.path.join(english_strings_directory, table), "w", encoding="utf-8"
            ) as table_file:
                table_file.write("")

    # We can't pass in too many files on the command line or the argument list
    # is too long. To avoid this, we do it in chunks of 500.
    # Using larger chunks reduces subprocess overhead significantly.
    files_per_iteration = 500

    # Create chunks
    chunks = []
    for i in range(0, (len(file_paths) // files_per_iteration) + 1):
        current_files = file_paths[i * files_per_iteration : (i + 1) * files_per_iteration]
        if current_files:
            chunks.append(current_files)

    # Process chunks in parallel
    with ThreadPoolExecutor(max_workers=min(max_workers, len(chunks))) as executor:
        futures = {
            executor.submit(_extract_strings, chunk, english_strings_directory): chunk
            for chunk in chunks
        }
        for future in as_completed(futures):
            error = future.result()
            if error:
                raise DotStringsException(error)

    # Convert all .strings files to UTF-8 in parallel
    strings_files = [
        os.path.join(english_strings_directory, file_name)
        for file_name in os.listdir(english_strings_directory)
        if file_name.endswith(".strings")
        and os.path.isfile(os.path.join(english_strings_directory, file_name))
    ]

    with ThreadPoolExecutor(max_workers=min(max_workers, len(strings_files))) as executor:
        futures = {
            executor.submit(_convert_to_utf8, file_path): file_path for file_path in strings_files
        }
        for future in as_completed(futures):
            future.result()  # Raise any exceptions that occurred
