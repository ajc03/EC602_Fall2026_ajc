# pygrep — Specification

`pygrep` searches text files for lines matching a pattern and writes the
matching lines to standard output.

The key words MUST, SHOULD, and MAY mean (respectively): is required for a conforming implementation, is a recommendation that does not change observable behavior, and is permitted.

---

## 1. Command line

### 1.1 Synopsis

```
pygrep [OPTION]... PATTERN [FILE]...
```

### 1.2 Operands

| Operand | Meaning |
| --- | --- |
| `PATTERN` | Required. The first non-option argument. |
| `FILE` | Zero or more paths to search. |

If zero `FILE` operands are given, `pygrep` reads standard input.

The same path MAY appear more than once. It is opened and searched once per
occurrence, and each occurrence produces its own output.

### 1.3 Options

Only the following options exist. Every other argument beginning with `-` is a usage error.

| Option | Long form | Meaning |
| --- | --- | --- |
| `-i` | `--ignore-case` | Match regardless of case. |
| `-v` | `--invert-match` | Select the lines that do *NOT* match. |
| `-n` | `--line-number` | Prefix each output line with its line number. |
| `-c` | `--count` | Suppress normal output, print a count of selected lines per file. |
| `-l` | `--files-with-matches` | Suppress normal output, print the name of each file with at least one selected line. |
| `-h` | `--help` | Print usage to standard output and exit 0. |

Options do NOT need to appear in a specific order

**NOTE:** `pygrep` REQUIRES filename suffixes. `pygrep -n beta a.txt` is valid, but `pygrep -n beta a` is *NOT*.

### 1.4 How the selecting options combine

Two options change *what* is selected:

- `-i` and `-v` are independent and may be combined. Using both selects the lines that do not match the pattern regardless of letter case.

Three options change *how* the result is reported: normal output, `-c`, `-l`. Exactly one reporting mode is in effect. When more than one is requested, the mode is chosen by this precedence, **highest first**:

1. `-l`
2. `-c`
3. normal output

The order the options appear on the command line has no effect. `-c -l` and `-l -c` both behave as `-l`.

`-n` applies only to normal output. Under `-c` or `-l` it is accepted and ignored — `-n -c` prints exactly what `-c` prints.

`-i` and `-v` can both be used with `-n`,`-c`, and `-l`. For example, if `-i` is used with `-l` all files with matches are printed regardless of case (if `red` is searched, files with `Red` or `red` will be printed).

Each option does not need to be typed with a seperate `-`. Example: `-iv` is valid and equivalent to `-i -v` and `-v -i`.

### 1.5 The pattern

- A line is a match if the pattern matches anywhere in it.
- The text searched is the line exactly as read, *including* its trailing newline. A pattern is therefore able to match across that newline, though a pattern containing one is unusual.
- If `-i` is used, the comparison is made with both the line and the pattern set to lower case, but the line is printed in its original case.
- An empty pattern is valid.

### 1.6 Usage errors

It is a usage error if:

- no arguments are given at all
- every argument is an option, so no `PATTERN` operand is present
- an unrecognized option is given (for example `-z` or `--color`).

In each case `pygrep` MUST write a usage message to standard error, write nothing to standard output, and exit 2.

`-h` / `--help` is not an error: the usage message goes to standard **output** and the exit status is 0. No search is performed, even if a pattern is present.

---

## 2. Output

All normal output goes to standard output. Every line written to standard output MUST be terminated by a single newline (`\n`), including the last one.

### 2.1 Field separator

Fields within an output line are separated by a single colon `:` with no surrounding spaces. Line content is never modified, truncated, quoted, or escaped. The only change made to a line before printing is the removal of its trailing newline, so leading and trialing spaces and tabs are preserved exactly.

### 2.2 When the filename is printed

The filename prefix is printed **if and only if two or more `FILE` operands were given on the command line.**

This is decided by the command line alone. It does not matter how many of those files existed, how many were readable, or how many produced output. `pygrep p a.txt missing.txt` prints a prefix on its matches from `a.txt` even though `missing.txt` could not be opened.

With zero or one `FILE` operand, no prefix is printed.

The name printed is the operand string exactly as it was given on the command line. If the operand was `./a.txt`, the prefix is `./a.txt`.

### 2.3 Normal output

One output line per selected line.

| Options | Format |
| --- | --- |
| (none) | `LINE` |
| `-n` | `LINENUM:LINE` |
| (none), 2+ files | `FILE:LINE` |
| `-n`, 2+ files | `FILE:LINENUM:LINE` |

`LINENUM` is the 1-based index of the line within its own file. The counter restarts at 1 for each file. It counts every line read, not only the selected ones, and is unaffected by `-v`.

Example: with `a.txt` containing `alpha\nbeta\nAlpha\ngamma\n` and `b.txt`
containing `beta\ndelta\n`:

```
$ pygrep beta a.txt
nbeta

$ pygrep -n beta a.txt
2:nbeta

$ pygrep beta a.txt b.txt
a.txt:nbeta
b.txt:beta

$ pygrep -n beta a.txt b.txt
a.txt:2:beta
b.txt:1:beta
```

### 2.4 `-c` output

One output line per file operand, in command-line order, whether or not the count is zero.

| Options | Format |
| --- | --- |
| `-c` | `COUNT` |
| `-c`, 2+ files | `FILE:COUNT` |

`COUNT` is the number of selected lines in that file, written in decimal with no padding and no sign. Under `-v` it is the number of non-matching lines.

A file that could not be opened produces **no** count line at all. It produces only the error on standard error. It is not reported as `0`.

```
$ pygrep -c beta a.txt
1

$ pygrep -c beta a.txt b.txt
a.txt:1
b.txt:1

$ pygrep -c -n beta a.txt b.txt        # -n ignored
a.txt:1
b.txt:1
```

Note that `-c` prints `0` for a file with no selected lines, but printing `0` does not by itself make the exit status 0.

### 2.5 `-l` output

One output line per file that has **at least one** selected line, in command-line order. The line is the filename alone, with no count, no colon and no line content — the name is always printed, even for a single file operand.

```
$ pygrep -l beta a.txt
a.txt

$ pygrep -l beta a.txt b.txt
a.txt
b.txt

$ pygrep -l zzz a.txt b.txt
                                     # nothing
```

A file with zero selected lines produces no output line. A file that could not be opened produces no output line.

The implementation SHOULD stop reading a file as soon as its first line is selected, since the rest cannot change the output.

### 2.6 Ordering and flushing

Files MUST be processed strictly in command-line order, and lines within a file in file order. Output MUST NOT be reordered or buffered across files in a way that changes the order seen by a user.

---

## 3. Edge cases

### 3.1 Empty pattern

An empty pattern is valid. It matches at position 0 of every line, so every line is selected (including empty lines).

```
$ pygrep "" a.txt          $ pygrep -c "" a.txt        $ pygrep -v -c "" a.txt
alpha                      4                           0
beta                                                   # exit 1
Alpha
gamma
# exit 0
```

With `-v`, an empty pattern selects nothing, so standard output is empty (or `0` under `-c`) and the exit status is 1.

### 3.2 Empty file

A zero-byte file contains zero lines. Nothing is selected from it.

- normal output: nothing
- `-c`: the count line, with count `0`
- `-l`: nothing

An empty file is not an error. If it is the only file, the exit status is 1.

```
$ pygrep -c anything empty.txt
0
# exit 1
```

**A file containing only `\n` is different**: it contains one line, which is empty. `pygrep -c "" onlynewline.txt` prints `1`.

### 3.3 Last line with no newline

The final line of such a file is a real line and is searched normally. Its content is everything after the last `\n`, or the whole file if there is none.

If that line is selected and printed, `pygrep` terminates i with `\n` anyway, because every line of output is newline-terminated. A file of the 17 bytes `no newline at end` therefore produces 18 bytes of output.

A zero-byte file is not treated as having a final empty line.

### 3.4 File that does not exist

`pygrep` writes one error line to standard error, produces no standard output for that file, and continues with the remaining files.

### 3.5 Directory given as a file

A directory operand is an error, exactly like a missing file: an error line on standard error, no output for that operand, processing continues.

### 3.6 File that exists but cannot be opened

Treated exactly like a file that does not exist: error line, continue, exit 2.

### 3.7 No file operands

`pygrep` reads standard input. This is not an error, and it is not a usage error: a command line with a pattern and no files is valid.

### 3.8 No file operands

A usage error: a message on standard error, nothing on standard output, exit 2. `pygrep` MUST NOT read a standard input in this case, because no `PATTERN` was given.

### 3.9 Pattern that looks like an option

The first argument that is not an option is the pattern, so `pygrep -x file` is an unrecognized-option usage error, not a search for `-x`. Use `--` to end option parsing: `pygrep -- -x dash.txt`.

---

## 4. Standard error

Standard error receives diagnostics only. It MUST never receive matching lines, counts, or filenames-as-results. Nothing at all is written to standard error on a successful run, including a run that finds no matches.

Every diagnostic line is terminated by `\n`.

### 4.1 Per-file errors

Format:

```
pygrep: FILE: MESSAGE
```

`FILE` is the operand. `MESSAGE` is the system error description. The three required messages:

| Condition | Line |
| --- | --- |
| Path does not exist | `pygrep: nope.txt: No such file or directory` |
| Path is a directory | `pygrep: adir: Is a directory` |
| Path not readable | `pygrep: secret.txt: Permission denied` |

**Note:** The line message can be some variation of what is written in the table. The messages do not need to match exactly.

Any other `OSError` uses that error's own description in the same three-field shape. One line per failing operand. `pygrep` MUST continue to the next operand after writing it.

### 4.2 Usage errors

A usage error takes one of two forms on standard error:

A **missing** `PATTERN`, including the case of no arguments at all, is reported by `argparse` as two lines:

```
usage: pygrep [-i] [-v] [-n] [-c] [-l] PATTERN [FILE]...
pygrep: error: the following arguments are required: pattern
```

**An unrecognized option** is reported as one line:

```
pygrep: Unrecognized option, use -h or --help for available options
```

Both exit 2 and write nothing to standard output.

### 4.3 Standard input

When `pygrep` reads standard input, the name used for it - in `-l` output and in any diagnostic - is the literal string:

```
(standard input)
```

Because standard input is read only when there are no `FILE` operands, and the filename prefix requires two or more operands, this name is visible only under `-l`:

```
$ printf 'beta\n' | pygrep -l beta
(standard input)

$ printf 'beta\n' | pygrep -n beta
1:beta
```

---

## 5. Exit status

Exactly one status is returned:

| Status | Meaning |
| --- | --- |
| `0` | At least one line was selected in at least one file. |
| `1` | No line was selected anywhere and no error occurred. |
| `2` | An error occurred. |

The rules (in order of precedence):

1. If any usage error occurred, the status is **2**.
2. Otherwise, if any file operand produced a per-file error, the status is **2** — **even if other files produced matches, and even if output was written to standard output.**
3. Otherwise, if the total number of selected lines across all files is greater than zero, the status is **0**.
4. Otherwise the status is **1**.

Notes that follow from these rules:

- Under `-v`, "selected" means "non-matching", so `pygrep -v "" a.txt` exits 1.
- Under `-c`, printing `0` still means nothing was selected: `pygrep -c zzz a.txt` prints `0` and exits **1**.
- Under `-l`, the status is 0 if and only if at least one filename was printed.
- `-h`/`--help` exits **0**.
- An empty file, or a file with no matches, is not an error and never by itself causes exit status 2.

---

## 6. Test cases

Fixtures used below. Contents are given as Python string literals so that
newlines are unambiguous.

| File | Contents |
| --- | --- |
| `alpha.txt` | `"alpha\nbeta\nAlpha\ngamma\n"` |
| `beta.txt` | `"beta\ndelta\n"` |
| `b.txt` | `"pie\napple pie\n"` |
| `empty.txt` | `""` (zero bytes) |
| `nonl.txt` | `"no newline at end"` (no trailing newline) |
| `dash.txt` | `"has -x here\n"` |
| `ind.txt` | `"    indented match\nplain match\n"` |
| `adir/` | a directory, empty |
| `nope.txt` | does not exist |

In the expectations, `""` means the stream is empty (zero bytes). Every non-empty stdout shown ends with a newline.

---

**Test 1 — plain match, one file**
- given: `alpha.txt`
- run: `pygrep beta alpha.txt`
- expect: stdout `"beta\n"` · stderr `""` · exit `0`

**Test 2 — no match, one file**
- given: `alpha.txt`
- run: `pygrep zzz alpha.txt`
- expect: stdout `""` · stderr `""` · exit `1`

**Test 3 — filename prefix appears with two files**
- given: `alpha.txt`, `b.txt`
- run: `pygrep beta alpha.txt b.txt`
- expect: stdout `"alpha.txt:beta\nb.txt:beta\n"` · stderr `""` · exit `0`

**Test 4 — line numbers, one file (no prefix)**
- given: `alpha.txt`
- run: `pygrep -n beta alpha.txt`
- expect: stdout `"2:beta\n"` · stderr `""` · exit `0`

**Test 5 — line numbers restart per file, prefix present**
- given: `alpha.txt`, `b.txt`
- run: `pygrep -n beta alpha.txt b.txt`
- expect: stdout `"alpha.txt:2:beta\nb.txt:1:beta\n"` · stderr `""` · exit `0`

**Test 6 — `-c` with `-n`: `-n` is ignored**
- given: `alpha.txt`, `b.txt`
- run: `pygrep -c -n beta alpha.txt b.txt`
- expect: stdout `"alpha.txt:1\nb.txt:1\n"` · stderr `""` · exit `0`

**Test 7 — `-l` beats `-c`, in either order**
- given: `alpha.txt`, `b.txt`
- run: `pygrep -c -l beta alpha.txt b.txt`
- expect: stdout `"alpha.txt\nb.txt\n"` · stderr `""` · exit `0`
- run: `pygrep -l -c beta alpha.txt b.txt`
- expect: identical to the above

**Test 8 — `-c` prints 0 but the exit status is 1**
- given: `empty.txt`
- run: `pygrep -c anything empty.txt`
- expect: stdout `"0\n"` · stderr `""` · exit `1`

**Test 9 — empty pattern matches every line**
- given: `alpha.txt`
- run: `pygrep -c "" alpha.txt`
- expect: stdout `"4\n"` · stderr `""` · exit `0`

**Test 10 — empty pattern inverted selects nothing**
- given: `alpha.txt`
- run: `pygrep -v "" alpha.txt`
- expect: stdout `""` · stderr `""` · exit `1`

**Test 11 — unterminated last line is matched and newline-terminated on output**
- given: `nonl.txt`
- run: `pygrep newline nonl.txt`
- expect: stdout is exactly the 18 bytes `"no newline at end\n"` · stderr `""`
  · exit `0`

**Test 12 — file that does not exist**
- given: nothing
- run: `pygrep beta nope.txt`
- expect: stdout `""` · stderr `"pygrep: nope.txt: No such file or
  directory\n"` · exit `2`

**Test 13 — a match plus a missing file still exits 2, and the prefix appears**
- given: `alpha.txt`
- run: `pygrep beta alpha.txt nope.txt`
- expect: stdout `"alpha.txt:beta\n"` · stderr `"pygrep: nope.txt: No such file or
  directory\n"` · exit `2`

**Test 14 — directory operand**
- given: `adir/`
- run: `pygrep beta adir`
- expect: stdout `""` · stderr `"pygrep: adir: Is a directory\n"` · exit `2`

**Test 15 — no file operands: read standard input, no prefix**
- given: stdin is `"beta\ngamma\n"`
- run: `pygrep -n beta`
- expect: stdout `"1:beta\n"` · stderr `""` · exit `0`

**Test 16 — `-l` on standard input uses the placeholder name**
- given: stdin is `"beta\n"`
- run: `pygrep -l beta`
- expect: stdout `"(standard input)\n"` · stderr `""` · exit `0`

**Test 17 — no arguments is a usage error, and stdin is not read**
- given: stdin is `"beta\n"`
- run: `pygrep`
- expect: stdout `""` · stderr begins with `"usage: pygrep "` and its second
  line begins with `"pygrep: error: "` · exit `2`

**Test 18 — case-insensitive matching**
- given: `alpha.txt`
- run: `pygrep -i alpha alpha.txt`
- expect: stdout `"alpha\nAlpha\n"` · stderr `""` · exit `0`

**Test 19 — invert with count**
- given: `alpha.txt`
- run: `pygrep -vc beta alpha.txt`
- expect: stdout `"3\n"` · stderr `""` · exit `0`

**Test 20 — `--` lets a pattern start with a dash**
- given: `dash.txt` containing `"has -x here\n"`
- run: `pygrep -- -x dash.txt`
- expect: stdout `"has -x here\n"` · stderr `""` · exit `0`

**Test 21 — `-l` prints the name even for a single file operand**
- given: `alpha.txt`
- run: `pygrep -l beta alpha.txt`
- expect: stdout `"alpha.txt\n"` · stderr `""` · exit `0`

**Test 22 — `-h` works even though `PATTERN` is required**
- given: nothing
- run: `pygrep -h`
- expect: stdout begins with `"usage: pygrep "` · stderr `""` · exit `0`

**Test 23 — `--help` behaves identically to `-h`**
- given: nothing
- run: `pygrep --help`
- expect: stdout begins with `"usage: pygrep "` · stderr `""` · exit `0`

**Test 24 — `-l` names a file once, however many lines are selected**
- given: `b.txt`
- run: `pygrep -l pie b.txt`
- expect: stdout `"b.txt\n"` · stderr `""` · exit `0`

**Test 25 — leading whitespace is preserved**
- given: `ind.txt`
- run: `pygrep match ind.txt`
- expect: stdout `"    indented match\nplain match\n"` · stderr `""` · exit `0`
