# Review of `lsp_gen.py`

Line numbers refer to the line numbers in `lsp_gen.py`, section numbers refer to sections in `SPEC.md`, and test names refer to tests in `test_lsp.py`. Each defect was confirmed in isolation.

## Defects

1. **Line 38 -** `"." in entry` hides every name that *contains* a dot, so `notes.txt` is missing from the default listing. §3 hides only names that *begin* with a dot. Confirmed in `test_04_middle_dot`.

2. **Lines 33-40 -** `-a` disables the filter but never adds `.` and `..`, so `lsp -a sub` prints nothing. §2 and §3 require that `-a` lists `.` and `..` even though `os.listdir()` does not return them. Confirmed in `test_F_all_on_empty_directory`.

3. **Line 43 -** Sorts with `key=lambda s: s.lower()`, so `apple` lists before `Banana`. §3 requires code point order, the default order of `sorted()`, in which `Banana` comes first. Confirmed in `test_01_default_lists_visible_entries_in_code_point_order`.

4. **Line 47 -** `result[::-1]` builds a reversed copy and discards it, so `-r` has no effect. §3 requires `-r` to reverse the sorted list. Confirmed in `test_05_dash_r`.

5. **Line 67 -** The size is `os.path.getsize(path) // 1024`, kibibytes rounded down, so `apple` (5 bytes) shows `0`. §4 requires that `SIZE` is `st_size` in bytes. Confirmed in `test_07_long_format_files`.

6. **Lines 75-78 -** `ArgumentParser` keeps its default `add_help=True`, so `-h` prints help and exits 0. §2 requires that `-h` is not an option of `lsp`, so `argparse` must reject it with status 2. Confirmed in `test_D_dash_h_error`.

7. **Line 108 -** The error line is printed to standard output. §5 requires that one line is printed to standard error, and nothing is printed to standard output. Confirmed in `test_09_missing_path_is_reported_on_stderr`.

8. **Line 109 -** `sys.exit(0)` after an error. §5 requires that status 1 is returned when `PATH` does not exist or cannot be read. Confirmed in `test_09_missing_path_is_reported_on_stderr`.

9. **Lines 106-108** Prins `No such file or directory` for all failures, so an unreadable directory is incorrectly reported as missing. §5 requires that `REASON` is `e.strerror`, which in this case should be `Permission denied`. Confirmed in `test_M_unreadable_directory`.

## Things to Change

1. **Line 19, mutable default -** `options=[]` is not a good idea. Change it to no default or a tuple. It is safe here only because the function never mutates the list. The first `options.append` inside it would leak between calls.

2. **Lines 34, 46, 89-96, 117: options rebuilt as a list of strings -** Should pass `args` itself, or the booleans. The strings duplicate the work `argparse` already did, and a misspelled `"I" in options` would be silently false while `args.I` would raise an error.

3. **Lines 36-37, 115-116: `for i in range(len(seq)): x = seq[i]` -** Should just iterate directly, `for x in seq:`. No reason for the extra steps.

4. **Lines 38, 91, 93, 95: comparisons to `True` and `False` -** These should be rewritten as `if args.a:` and `if not show_all:` respectively, since the values are already booleans.

5. **Lines 63, 67: the file is stat'ed twice -** Can just use `info.st_size` on line 67. This is only one system call instead of two, and makes sure the size does not come from a different moment than the mode and time printed next to it.

6. **Lines 100, 118: `os.path.isdir(args.path)` is evaluated twice -** It is better to decide once and keep that answer. This makes sure that the two checks do not disagree with each other if the path changes in between them.

7. **Lines 104-105: the list is built before the path is checked -** Should call `os.stat` first and then build `entries`. The current order only works because the handler exits.

8. **Line 106: bare `except:` -** This should be changed to `except OSError as e:`. A bare `except` will also catch the program's own bugs and `KeyboardInterrupt`. This means a typo inside `try` would be reported to the user as a missing file.

9. **Lines 112-113: `if len(entries) == 0: return` -** Should delete this. The loop does nothing for an empty list so this is pointless.

10. **Lines 73, 87, 109, 127: `main` reads `sys.argv`, calls `sys.exit`, and runs on import -** Should write `def main(argv=None)`, call `parse_args(argv)`, return the status, and end with `if __name__ == "__main__": sys.exit(main())`. The module can then be imported and tested in-process, and the exit status will then have only one source.

## Recommendation

This program should not be accepted. It violates the specification in multiple places, and several of those failures are invisible since it prints to standard output and exits 0. At least the defects listed above should be fixed. Specifically: filter with `startswith(".")`, under `-a` add `.` and `..` before sorting, sort with `.sort()` (puts `.` and `..` in required order), use `.reverse()` for `-r`, report `info.st_size`, replace the handler with `except OSError as e` that prints `e.strerror` to standard error and exits 1, and pass `add_help=False` with an explicit `--help` argument. While those are being fixed, the items listed under "Things to Change" should also be changed, though they do not block the acceptance of the program.