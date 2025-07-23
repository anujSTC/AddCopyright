import os
import sys

# Define a set of supported file extensions for efficient lookup
SUPPORTED_EXTENSIONS = {
    "py", "java", "js", "ts", "c", "cpp", "h", "hpp", "cs", "go", "rs",
    "html", "css", "scss", "sh", "rb", "php", "yml"
}

# Map of file extensions to their comment syntax.
# The tuple contains the start and end markers for a block comment.
# For languages that only use line-based comments, the end marker is an empty string,
# signifying that the start marker should be applied to each line of the notice.
COMMENT_MAP = {
    # C-style block comments (/* ... */)
    "c":    ("/*", " */"), "cpp":  ("/*", " */"), "h":    ("/*", " */"),
    "hpp":  ("/*", " */"), "java": ("/*", " */"), "js":   ("/*", " */"),
    "ts":   ("/*", " */"), "cs":   ("/*", " */"), "go":   ("/*", " */"),
    "rs":   ("/*", " */"), "css":  ("/*", " */"), "scss": ("/*", " */"),
    "php":  ("/*", " */"),

    # Hash-based line comments (# ...)
    "py":   ("#", ""), "sh":   ("#", ""), "rb":   ("#", ""), "yml": ("#", ""),

    # HTML/XML style comments (<!-- ... -->)
    "html": ("<!--", " -->"),
}

def prepend_copyright(file_path, copyright_text, comment_map):
    """
    Prepends a copyright notice to a file, formatted with the correct comment syntax.

    It handles files with shebangs or other special first lines, and avoids
    adding a copyright notice if one already seems to exist.

    Args:
        file_path (str): The full path to the file.
        copyright_text (str): The text of the copyright notice.
        comment_map (dict): A map of file extensions to comment syntax.
    """
    try:
        filename = os.path.basename(file_path)
        extension = os.path.splitext(file_path)[1].lstrip('.')

        # Handle special filenames that don't have extensions
        if filename == "Dockerfile":
            extension = "dockerfile"

        if extension not in comment_map:
            print(f"Warning: No comment style for '{extension}'. Skipping {file_path}", file=sys.stderr)
            return

        start_marker, end_marker = comment_map[extension]
        copyright_lines = copyright_text.strip().split('\n')

        # Format the notice based on comment style
        if end_marker:  # Block comment style
            notice = [f"{start_marker}"]
            notice.extend([f" * {line}".rstrip() for line in copyright_lines])
            notice.append(f" {end_marker}")
        else:  # Line-by-line comment style
            notice = [f"{start_marker} {line}".rstrip() for line in copyright_lines]
        formatted_notice = "\n".join(notice) + "\n"

        with open(file_path, 'r+', encoding='utf-8') as f:
            original_content = f.readlines()

            if any("Copyright (c)" in line for line in original_content[:20]):
                print(f"Copyright notice already found in {file_path}. Skipping.")
                return

            # Handle special first lines (shebang, PHP tag, etc.)
            first_line = ""
            content_to_prepend_to = original_content
            if original_content:
                line1 = original_content[0]
                if (line1.startswith("#!") or line1.strip().startswith("<?php") or
                   (extension == 'html' and line1.lower().startswith("<!doctype"))):
                    first_line = line1
                    content_to_prepend_to = original_content[1:]

            f.seek(0)
            f.truncate()
            if first_line:
                f.write(first_line)
            f.write(formatted_notice)
            # Only add a blank line for separation if there was other content in the file.
            if content_to_prepend_to:
                f.write("\n")
                f.writelines(content_to_prepend_to)

        print(f"Successfully added copyright to {file_path}")

    except Exception as e:
        print(f"Error processing file {file_path}: {e}", file=sys.stderr)

def find_files_by_extensions(root_dir, extensions_str, excluded_dirs=None):
    """
    Searches for files with specific extensions within a directory tree, skipping excluded directories.

    Args:
        root_dir (str): The path to the root directory of the search.
        extensions_str (str): A comma-separated string of file extensions to search for (e.g., "py,js").
        excluded_dirs (set): A set of directory names to exclude from the search (e.g., {'venv', '.git'}).

    Returns:
        list: A list of full paths to files matching any of the extensions.
    """
    matching_files = []
    if not os.path.isdir(root_dir):
        return matching_files

    if excluded_dirs is None:
        excluded_dirs = set()

    # Use a set for efficient lookups
    extensions = {ext.strip() for ext in extensions_str.split(",")}

    for dirpath, dirnames, filenames in os.walk(root_dir, topdown=True):
        # Prune the directories to be searched by modifying dirnames in-place.
        # This is the standard way to prevent os.walk from descending into certain folders.
        dirnames[:] = [d for d in dirnames if d not in excluded_dirs]

        for filename in filenames:
            # Handle special filenames that don't use extensions (e.g., Dockerfile)
            if "dockerfile" in extensions and filename == "Dockerfile":
                matching_files.append(os.path.join(dirpath, filename))
                continue  # Found, so move to the next file in the directory

            # Handle regular extensions
            file_ext = os.path.splitext(filename)[1].lstrip('.')
            if file_ext in extensions:
                matching_files.append(os.path.join(dirpath, filename))

    return matching_files


if __name__ == "__main__":
    directory_to_search = input("Enter the directory to search: ")
    file_extensions_str = input("Enter the file extensions to search for (comma-separated, no dots): ")
    excluded_dirs_str = input("Enter directories to exclude (comma-separated, e.g. venv,.git,build): ")

    # Parse excluded directories into a set for efficient lookup
    excluded_dirs = {d.strip() for d in excluded_dirs_str.split(',') if d.strip()}

    # Validate user-provided extensions against the supported list
    user_extensions = {ext.strip() for ext in file_extensions_str.split(",")}
    unsupported_extensions = user_extensions - SUPPORTED_EXTENSIONS

    if unsupported_extensions:
        print(f"Error: Unsupported file extensions provided: {', '.join(unsupported_extensions)}", file=sys.stderr)
        print(f"Supported extensions are: {', '.join(sorted(list(SUPPORTED_EXTENSIONS)))}", file=sys.stderr)
        sys.exit(1)

    # Read copyright text from file
    copyright_file = "copyright.txt"
    try:
        with open(copyright_file, 'r', encoding='utf-8') as f:
            copyright_text = f.read()
    except FileNotFoundError:
        print(f"Error: Copyright file '{copyright_file}' not found.", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading copyright file: {e}", file=sys.stderr)
        sys.exit(1)

    found_files = find_files_by_extensions(directory_to_search, file_extensions_str, excluded_dirs)

    if found_files:
        print(f"\nFound {len(found_files)} files. Adding copyright notice...")
        for file_path in found_files:
            prepend_copyright(file_path, copyright_text, COMMENT_MAP)
        print("\nCopyright addition process complete.")
    else:
        print(f"No files with extensions '{file_extensions_str}' found in '{directory_to_search}', or the directory is invalid.")
