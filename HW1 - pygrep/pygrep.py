#!/usr/bin/env python3

"AJ Chiaravalloti's pygrep for Homework 1"

import sys
import argparse
from pathlib import Path

def main(argv=None):
    # Define the arguments
    p = argparse.ArgumentParser(prog="pygrep", add_help=False, exit_on_error=False)
    p.add_argument("-i", "--ignore-case", action="store_true", help="Ignore letter cases when matching")
    p.add_argument("-v", "--invert-match", action="store_true", help="Return lines that do NOT match the pattern instead of lines that DO match")
    p.add_argument("-n", "--line-number", action="store_true", help="Print the line number of each matching line before the line itself")
    p.add_argument("-c", "--count", action="store_true", help="Prints the count of matching lines for each file instead of the matching lines themselves")
    p.add_argument("-l", "--file-with-matches", action="store_true", help="Prints the name of each file that contains at least one matching line instead of the matching line themselves")
    p.add_argument("-h", "--help", action="help", help="Prints the help message and exits")
    p.add_argument("pattern", help="The pattern that pygrep searches for in the specified files")
    p.add_argument("files", nargs="*", help="The files that pygrep searches in for the specified pattern")
    try:
        args, unknown = p.parse_known_args(argv)
    except argparse.ArgumentError as e:
        print(f"pygrep: {e}", file=sys.stderr)   # Need at least a pattern and a file name, this uses the error that is already generated
        return 2
    if unknown:             # Check if there are any unkown arguments. If so, it must be because an option not specified was used so throw the following error
        print("pygrep: Unrecognized option, use -h or --help for available options", file=sys.stderr)
        return 2
    linesnotprinted = 0     # Tracks the total number of lines not printed (or that did not contain the specified pattern)
    totallinenumbers = 0    # Tracks the total number of line numbers between all opened files
    anyerrors = 0           # If 0, means there were no errors. If greater than 0, means there was at least one error
    targets = args.files or [None]
    for file in targets:
        line_number = 0     # Tracks what line program is on
        count = 0           # Count number of the '-c' option
        linetemp = ""       # Needed later for ignore-case scenarios
        if file is None:    # If there is no file, want the standard input (keep the program running and let users type whatever string they want)
            name = "(standard input)"
            f = sys.stdin
            opened = False
        else:
            name = file
            # If the specified file is not actually a file, but a directory, want to print an error message but continue
            if Path(file).is_dir():
                print(f"pygrep: {file}: Is a directory", file=sys.stderr)
                anyerrors += 1
                continue
            # If any of the specified files do not exist, want to print an error message but continue the program
            elif not Path(file).is_file():
                print(f"pygrep: {file}: No such file or directory", file=sys.stderr)
                anyerrors += 1
                continue
            # Try to open the file and continue
            try:
                f = open(file, "r")
            except OSError as e:    # This line is here if any of the files cannot be opened for some reason
                print(f"pygrep: {file}: {e.strerror}", file=sys.stderr)
                anyerrors += 1
                continue
            opened = True
        try:
            for line in f:
                line_number += 1
                content = line.rstrip("\n") # Create a content value that strips the righthand newline off of each line, which avoids removing other whitespace like '.strip()' would
                if args.ignore_case:    # If ignore-case then set the current line and the pattern to lower-case (through a temporary value so that we can still print the real value in the file)
                    linetemp = line.lower()
                    pattern = args.pattern.lower()
                else:                   # Otherwise the temporary values are just the actual values in the document and specified
                    linetemp = line
                    pattern = args.pattern
                if args.invert_match:   # If -v, want to check if the pattern is NOT there
                    if pattern not in linetemp:
                        if args.file_with_matches:  # Check for -l first. Break if this runs
                            print(name)
                            break
                        elif args.count:            # Check for -c next and add to count
                            count += 1
                        elif len(args.files) > 1:   # If more than one file then ned to print file name as well
                            if args.line_number:    # If -n then need to specify line number as well
                                print(f"{name}:{line_number}:{content}")
                            else:
                                print(f"{name}:{content}")
                        elif args.line_number:      # Same as above if theres -n but only one file 
                            print(f"{line_number}:{content}")
                        else:                       # Otherwise
                            print(content)
                    else:
                        linesnotprinted += 1        # Add to he number of lines not printed for later and continue
                        continue
                else:
                    if pattern in linetemp: # If not -v, want to check if the pattern IS there. Everything below if the same as above
                        if args.file_with_matches:
                            print(name)
                            break
                        elif args.count:
                            count += 1
                        elif len(args.files) > 1:
                            if args.line_number:
                                print(f"{name}:{line_number}:{content}")
                            else:
                                print(f"{name}:{content}")
                        elif args.line_number:
                            print(f"{line_number}:{content}")
                        else:
                            print(content)
                    else:
                        linesnotprinted += 1
                        continue
        finally:
            if opened:
                f.close()
        if args.count and not args.file_with_matches:   # If we have -c and NOT -l, then want to print the count
            if len(args.files) > 1:                     # Also print the name of the file if there are multiple
                print(f"{name}:{count}")
            else:
                print(f"{count}")
        totallinenumbers += line_number         # Do this at the end to add the total number of lines in the file (line_number will be the total number of lines in the specific file)
    if anyerrors > 0:                           # Check if there were any errors, if so than program should return 2
        return 2
    elif linesnotprinted == totallinenumbers:   # Check if nothing was printed (by checking if total number of lines and number of lines not printed is equal). If so, return 1
        return 1
    else:                                       # If neither of the above are true, then just return 0 (no errors and something was printed)
        return 0

if __name__ == "__main__":
    sys.exit(main())