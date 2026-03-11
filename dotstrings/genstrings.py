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


def _clear_existing_strings(english_strings_directory: str) -> None:
    """Clear existing .strings files in the directory.

    :param english_strings_directory: Directory to clear .strings files from
    """
    for table in os.listdir(english_strings_directory):
        # Do not clear non .strings files
        if not table.endswith(".strings"):
            continue
        table_path = os.path.join(english_strings_directory, table)
        with open(table_path, "w", encoding="utf-8") as table_file:
            table_file.write("")


def _create_file_chunks(file_paths: list[str], chunk_size: int) -> list[list[str]]:
    """Split file paths into chunks.

    :param file_paths: List of file paths to split
    :param chunk_size: Size of each chunk
    :return: List of file path chunks
    """
    chunks = []
    for i in range(0, len(file_paths), chunk_size):
        chunks.append(file_paths[i : i + chunk_size])
    return chunks


def _get_strings_files(english_strings_directory: str) -> list[str]:
    """Get all .strings file paths in the directory.

    :param english_strings_directory: Directory to search
    :return: List of .strings file paths
    """
    strings_files = []
    for file_name in os.listdir(english_strings_directory):
        file_path = os.path.join(english_strings_directory, file_name)
        # Check for file type and .strings extension
        if file_name.endswith(".strings") and os.path.isfile(file_path):
            strings_files.append(file_path)
    return strings_files


def _process_chunks(
    chunks: list[list[str]], english_strings_directory: str, max_workers: int
) -> None:
    """Process chunks of files in parallel.

    :param chunks: List of file chunks to process
    :param english_strings_directory: Directory for output
    :param max_workers: Number of workers to use
    """
    temp_dirs = []

    try:
        with ThreadPoolExecutor(max_workers=min(max_workers, len(chunks))) as executor:
            # Create temporary directories for each chunk so that we can process in parallel without file conflicts
            for _ in chunks:
                temp_dir = tempfile.mkdtemp()
                temp_dirs.append(temp_dir)

            # Submit tasks with their own temp directories
            futures = {
                executor.submit(_extract_strings, chunk, temp_dir): (chunk, temp_dir)
                for chunk, temp_dir in zip(chunks, temp_dirs)
            }

            for future in as_completed(futures):
                future.result()  # Raise any exceptions that occurred

        # Merge all temp directories into final output
        for temp_dir in temp_dirs:
            for file_name in os.listdir(temp_dir):
                if not file_name.endswith(".strings"):
                    continue

                temp_file_path = os.path.join(temp_dir, file_name)
                final_file_path = os.path.join(english_strings_directory, file_name)

                # Read content from temp file
                with open(temp_file_path, "r", encoding="utf-16") as temp_file:
                    content = temp_file.read()

                # Append to final file
                with open(final_file_path, "a", encoding="utf-16") as final_file:
                    final_file.write(content)

    finally:
        # Clean up temporary directories
        for temp_dir in temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir)


def _convert_strings_files(strings_files: list[str], max_workers: int) -> None:
    """Convert .strings files to UTF-8 in parallel.

    :param strings_files: List of .strings file paths to convert
    :param max_workers: Number of workers to use
    """
    with ThreadPoolExecutor(max_workers=min(max_workers, len(strings_files))) as executor:
        futures = {
            executor.submit(_convert_to_utf8, file_path): file_path for file_path in strings_files
        }
        for future in as_completed(futures):
            future.result()  # Raise any exceptions that occurred


def _extract_strings(file_paths: list[str], english_strings_directory: str) -> None:
    """Extract strings for a chunk of files.

    :param list[str] file_paths: The files to extract strings from
    :param str english_strings_directory: The directory to place the extracted strings
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
            raise DotStringsException(f"Encountered an error generating strings: {output}")
    except subprocess.CalledProcessError as ex:
        raise DotStringsException(f"Unable generate .strings files! {ex}") from ex


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
        _clear_existing_strings(english_strings_directory)

    # We can't pass in too many files on the command line or the argument list
    # is too long. To avoid this, we do it in chunks of 500.
    # Using larger chunks reduces subprocess overhead significantly.
    chunks = _create_file_chunks(file_paths, chunk_size=500)

    # Process chunks in parallel
    _process_chunks(chunks, english_strings_directory, max_workers)

    # Convert all .strings files to UTF-8 in parallel
    strings_files = _get_strings_files(english_strings_directory)
    _convert_strings_files(strings_files, max_workers)
