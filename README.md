# Automatic Copyright Header Script

A Python script to automatically find source files and prepend a copyright notice to them, handling various programming language comment styles.

## Features

- **Recursive Scanning**: Scans a given directory and its subdirectories for specified file types.
- **Multi-Language Support**: Supports a wide range of languages with both block (`/* ... */`) and line-based (`# ...`) comments.
- **Customizable Notice**: The copyright notice is loaded from an external `copyright.txt` file, making it easy to manage and update.
- **Idempotent**: Intelligently skips files that already contain a copyright notice to prevent duplicate headers.
- **Preserves File Structure**: Correctly handles files with special first lines like shebangs (`#!/usr/bin/env python`), PHP tags (`<?php`), and HTML doctypes.
- **Directory Exclusion**: Allows you to exclude specific directories from the scan (e.g., `venv`, `.git`, `build`, `node_modules`).
- **Interactive CLI**: A simple, interactive command-line interface prompts for all necessary inputs.

## Prerequisites

- Python 3.6+

## Setup

1.  Place the `add_copyright.py` script in your project's root directory or a dedicated `tools` directory.

2.  Create a file named `copyright.txt` in the same directory as the script.

3.  Paste your desired copyright or license text into `copyright.txt`. The script will use this exact text for the header.

    **Example `copyright.txt`:**
    ```
    Copyright (c) 2025, Your Company or Name
    All rights reserved.

    Redistribution and use in source and binary forms, with or without
    modification, are permitted provided that the following conditions are met:

    * Redistributions of source code must retain the above copyright notice, this
      list of conditions and the following disclaimer.
    
    ... (rest of your license text) ...
    ```

## Usage

1.  Navigate to the directory containing the script and run it from your terminal:
    ```bash
    python add_copyright.py
    ```

2.  The script will then prompt you for the required information:
    - **The directory to search**: You can enter `.` to search the current directory.
    - **File extensions**: A comma-separated list of file extensions to process (e.g., `py,js,css,go`).
    - **Directories to exclude**: A comma-separated list of directories to ignore (e.g., `venv,.git,node_modules,build`).

### Example Session

```bash
$ python add_copyright.py

Enter the directory to search: .
Enter the file extensions to search for (comma-separated, no dots): py,js,html,css
Enter directories to exclude (comma-separated, e.g. venv,.git,build): venv,.git,dist

Found 42 files. Adding copyright notice...
Successfully added copyright to ./src/components/Header.js
Copyright notice already found in ./src/main.py. Skipping.
Successfully added copyright to ./public/index.html
...

Copyright addition process complete.
```

## Configuration & Extension

You can easily extend the script to support new file types by modifying the `SUPPORTED_EXTENSIONS` and `COMMENT_MAP` constants at the top of `add_copyright.py`.

### How to Add a New File Type

Let's say you want to add support for Swift (`.swift`) files, which use C-style block comments.

1.  **Add the extension to `SUPPORTED_EXTENSIONS`**:
    ```python
    SUPPORTED_EXTENSIONS = {
        "py", "java", "js", "ts", "c", "cpp", "h", "hpp", "cs", "go", "rs",
        "html", "css", "scss", "sh", "rb", "php", "yml", "dockerfile", "swift" # Add swift here
    }
    ```

2.  **Add the extension and its comment style to `COMMENT_MAP`**:
    ```python
    COMMENT_MAP = {
        # C-style block comments (/* ... */)
        "c":    ("/*", " */"), "cpp":  ("/*", " */"), "h":    ("/*", " */"),
        "hpp":  ("/*", " */"), "java": ("/*", " */"), "js":   ("/*", " */"),
        "ts":   ("/*", " */"), "cs":   ("/*", " */"), "go":   ("/*", " */"),
        "rs":   ("/*", " */"), "css":  ("/*", " */"), "scss": ("/*", " */"),
        "php":  ("/*", " */"), "swift": ("/*", " */"), # Add swift here

        # Hash-based line comments (# ...)
        "py":   ("#", ""), "sh":   ("#", ""), "rb":   ("#", ""), "yml": ("#", "")

        # HTML/XML style comments (<!-- ... -->)
        "html": ("<!--", " -->"),
    }
    ```