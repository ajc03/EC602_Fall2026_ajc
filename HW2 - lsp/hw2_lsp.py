#!/usr/bin/env python3
"""
lsp.py - A simple Python implementation of the ls command.

This script lists the contents of a directory, similar to the Unix `ls`
command. It supports the -a, -l and -r options as described in SPEC.md.

Usage:
    python lsp.py [-a] [-l] [-r] [PATH]
"""

import argparse
import os
import stat
import sys
import time


def get_entries(path, show_all, reverse):
    """
    Get the list of entries in the given directory.

    Args:
        path: The directory path to list.
        show_all: Option of whether to include hidden entries.
        reverse: Option of whether to reverse the sort order.

    Returns:
        A sorted list of entry names.
    """
    # Get all entries in the directory
    entries = os.listdir(path)

    # Filter out hidden files unless -a is specified
    result = [] # Replaced rid of show_all variable from options since this is clearer
    if show_all:
        result.append(".")  # Add "." first and then "..", as specified
        result.append("..") 
    for entry in entries:   # Go through entries, filter out hidden files, and add other files to list
        if not show_all and entry.startswith("."):
            continue
        result.append(entry)

    # Sort the entries in code point order
    result.sort()

    # Reverse the order if -r is specified
    if reverse: # Removed options and replaced with reverse variable
        result.reverse()    # Use .reverse instead of result[::-1]

    return result


def format_long(path, name):
    """
    Format a single entry in long format (like ls -l).

    Args:
        path: The full path to the entry.
        name: The display name of the entry.

    Returns:
        A formatted string with mode, size, modification time and name.
    """
    info = os.stat(path)
    # Get the permission string (e.g. -rw-r--r--)
    mode = stat.filemode(info.st_mode)
    # Get the file size in bytes
    size = info.st_size # Use info.st_size instead of .getsize since we do not want to stat twice
    # Format the modification time
    mtime = time.strftime("%Y-%m-%d %H:%M", time.localtime(info.st_mtime))
    return f"{mode} {size:8d} {mtime} {name}"


def main(argv=None):
    """Main entry point for the lsp command."""
    parser = argparse.ArgumentParser(
        prog="lsp",
        description="List a directory, one entry per line.",
        add_help=False  # Need to make sure -h does not work
    )
    parser.add_argument("path", nargs="?", default=".",
                        help="directory to list (default: current directory)")
    parser.add_argument("-a", action="store_true",
                        help="include hidden entries")
    parser.add_argument("-l", action="store_true",
                        help="use long listing format")
    parser.add_argument("-r", action="store_true",
                        help="reverse the sort order")
    parser.add_argument("--help", action="help",    # Add --help manually since --help should work but -h should not
                        help="Prints the help message and exits")
    args = parser.parse_args(argv)

    # Removed the entire options list and replaced it with individual variables

    is_dir = os.path.isdir(args.path)   # Moved this out of the try block since it is used twice but only want to check once
    try:
        if is_dir:
            entries = get_entries(args.path, args.a, args.r)
        else:
            os.stat(args.path)      # Reversed these so that os.stat occurs first
            entries = [args.path]
    except OSError as e:
        # Handle the case where the PATH is missing or cannot be read
        print(f"lsp: {args.path}: {e.strerror}", file=sys.stderr)   # Added file=sys.stderr to make sure this was detected as an error (used f-string just as a preference)
        return 1 # Added return 1 instead of exit 0 (since this is an error) and so that there is only one source of exit codes

    # Deleted pointless if len(entries) == 0 check (for loop does that anyways)

    for entry in entries:   # Go through the entries (no need for "i in range")
        try:    # Need this try block in-case there is a permission error
            if args.l:  # If the -l option is specified, print the long format
                if is_dir:     # Make full path of entry if the path is a directory
                    full_path = os.path.join(args.path, entry)
                else:   # Otherwise, just use the entry as the full path
                    full_path = entry
                print(format_long(full_path, entry))    # Either way, print the long format
            else:   # If -l option is not specified, just print the entry
                print(entry)
        except OSError as e:    # Exception for if there is an entry that cannot be stat'ed
            print(f"lsp: {args.path}: {e.strerror}", file=sys.stderr)
            return 1    # Change to return 1 so that there is only one source of exit codes
    return 0    # Added a return to the end of main()
        
if __name__ == "__main__": sys.exit(main()) # Added sys.exit(main()) to make sure the exit code is returned properly
