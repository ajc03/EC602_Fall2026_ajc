# pygrep — Specification

`pygrep` searches text files for lines matching a pattern and writes the
matching lines to standard output.

The key words MUST, MUST NOT, SHOULD and MAY are used in the usual sense: MUST
is required for a conforming implementation, SHOULD is a recommendation that
does not change observable behavior, MAY is permitted.

---

## 1. Command line

### 1.1 Synopsis

```
pygrep [OPTION]... PATTERN [FILE]...
```

### 1.2 Operands

| Operand | Meaning |
| --- | --- |
| `PATTERN` | Required. The first non-option argument. A regular expression (see §1.5). |
| `FILE` | Zero or more paths to search. The literal operand `-` means standard input. |

If zero `FILE` operands are given, `pygrep` reads standard input (§4.4).

The same path MAY appear more than once; it is opened and searched once per
occurrence, and each occurrence produces its own output.

### 1.3 Options

Only the following options exist. Every other argument beginning with `-` is a
usage error (§1.6).

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

### 1.5 The pattern

- A line is a match if the pattern matches anywhere in it.
- The line content passed to the matcher MUST NOT include the trailing newline. Therefore `$` matches at end of line and `pygrep a$ ` behaves as expected.
- If the pattern is not a valid regular expression, this is an error (§4.3).
- An empty pattern is NOT valid and WILL result in an error.

### 1.6 Usage errors

It is a usage error if:

- no arguments are given at all;
- every argument is an option, so no `PATTERN` operand is present;
- an unrecognized option is given (for example `-z` or `-color`).

In each case `pygrep` MUST write a usage message to standard error (§4.2), write nothing to standard output, and exit 2 (§5).

`-h` / `--help` is not an error: the usage message goes to standard **output** and the exit status is 0. No search is performed, even if a pattern is present.

---

## 2. Output

All normal output goes to standard output. Every line written to standard output MUST be terminated by a single newline (`\n`), including the last one.

### 2.1 Field separator

Fields within an output line are separated by a single colon `:` with no
surrounding spaces. Line content is never modified, truncated, quoted or
escaped.

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
| `-n` | `LINENO:LINE` |
| (none), 2+ files | `FILE:LINE` |
| `-n`, 2+ files | `FILE:LINENO:LINE` |

`LINENO` is the 1-based index of the line within its own file. The counter
restarts at 1 for each file. It counts every line read, not only the selected
ones, and is unaffected by `-v`.

Examples, with `a.txt` containing `alpha\nbeta\nAlpha\ngamma\n` and `b.txt`
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

A file that could not be opened (§3.4, §3.5) produces **no** count line at all. It produces only the error on standard error. It is not reported as `0`.

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

Note that `-c` prints `0` for a file with no selected lines, but printing `0` does not by itself make the exit status 0. See §5.

### 2.5 `-l` output

One output line per file that has **at least one** selected line, in command-line order. The line is the filename alone, with no count, no colon and no line content — the rule in §2.2 does not apply here, the name is always printed, even for a single file operand.

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

Files MUST be processed strictly in command-line order, and lines within a file in file order. Output MUST NOT be reordered or buffered across files in a way that changes the order seen by a users.

---

## 3. Edge cases

### 3.1 Empty pattern

An empty pattern is valid. It matches at position 0 of every line, so every
line is selected — including empty lines.

```
$ pygrep "" a.txt          $ pygrep -c "" a.txt        $ pygrep -vc "" a.txt
alpha                      4                           0
beta                                                   # exit 1
Alpha
gamma
# exit 0
```

With `-v`, an empty pattern selects nothing, so standard output is empty (or
`0` under `-c`) and the exit status is 1.

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

**A file containing only `\n` is different**: it contains one line, which is
empty. `pygrep -c "" onlynewline.txt` prints `1`.

### 3.3 Last line with no trailing newline

The final line of such a file is a real line and is searched normally. Its
content is everything after the last `\n`, or the whole file if there is none.

If that line is selected and printed, `pygrep` **terminates it with `\n`
anyway.** Output is always newline-terminated (§2). This matches GNU `grep`,
verified with `od -c`: given `nonl.txt` containing the 17 bytes
`no newline at end`, `grep newline nonl.txt` emits 18 bytes, ending `d \n`.

```
$ pygrep newline nonl.txt | od -c | tail -2
0000020   d  \n
0000022

$ pygrep -c newline nonl.txt
1
```

A zero-byte file is not treated as having a final empty line (§3.2).

### 3.4 File that does not exist

`pygrep` writes one error line to standard error (§4.1), produces no standard
output for that file, and continues with the remaining files. The final exit
status is 2 (§5).

### 3.5 Directory given as a file

**[Decision]** A directory operand is an error, exactly like a missing file: an
error line on standard error, no output for that operand, processing continues,
final exit status 2.

GNU `grep` behaves this way by default (`grep: adir: Is a directory`), but has
`-d`/`--directories` and `-r` to change it. `pygrep` has no such option and
never recurses. This keeps the tool a pure file-to-lines filter; recursion
belongs to the shell or to `find`.

### 3.6 File that exists but cannot be opened

Treated exactly as §3.4: error line, continue, exit 2. The distinct cases
(permission denied, is a directory, no such file) differ only in the message
text (§4.1).

### 3.7 No file operands

`pygrep` reads standard input. See §4.4 for how it is named and §5 for the
exit status. This is not an error, even if standard input is an interactive
terminal — in that case `pygrep` waits for input, as `grep` does.

### 3.8 No arguments at all

A usage error (§1.6): usage message on standard error, exit 2. `pygrep` MUST
NOT read standard input in this case.

### 3.9 Pattern that looks like an option

The first argument that is not an option is the pattern, so `pygrep -x file`
is an unrecognized-option usage error, not a search for `-x`. Use `--`:
`pygrep -- -x file`.

### 3.10 Text encoding and line splitting

**[Decision]** Input is decoded as UTF-8 with `errors="surrogateescape"`, and
output is encoded back the same way. Bytes that are not valid UTF-8 therefore
survive a round trip unchanged rather than raising or being replaced.

Lines are split on the single byte `\n` only. A `\r` is ordinary line content:
a CRLF file yields lines ending in `\r`, so `pygrep 'end$'` will not match a
line that reads `end\r`. `\r` alone is not a line separator.

**[Decision]** `pygrep` performs no binary-file detection. GNU `grep` prints
`Binary file X matches` and suppresses the content; `pygrep` always prints the
matching line. The rule "every selected line is printed" holds without
exception, which is far easier to test.

---

## 4. Standard error

Standard error receives diagnostics only. It MUST never receive matching lines,
counts or filenames-as-results. Nothing at all is written to standard error on
a successful run, including a run that finds no matches.

Every diagnostic line is terminated by `\n`.

### 4.1 Per-file errors

Format:

```
pygrep: FILE: MESSAGE
```

`FILE` is the operand exactly as given (§2.2). `MESSAGE` is the system error
description. The three required messages:

| Condition | Line |
| --- | --- |
| Path does not exist | `pygrep: nope.txt: No such file or directory` |
| Path is a directory | `pygrep: adir: Is a directory` |
| Path not readable | `pygrep: secret.txt: Permission denied` |

Any other `OSError` uses that error's own description in the same three-field
shape. One line per failing operand. `pygrep` MUST continue to the next operand
after writing it.

### 4.2 Usage errors

For a usage error (§1.6), standard error receives exactly:

```
usage: pygrep [-i] [-v] [-n] [-c] [-l] PATTERN [FILE]...
pygrep: error: MESSAGE
```

where `MESSAGE` names the problem, for example `the following arguments are
required: PATTERN` or `unrecognized arguments: -z`.

### 4.3 Invalid pattern

```
pygrep: invalid pattern: DETAIL
```

`DETAIL` is the message from `re.error`, for example `nothing to repeat at
position 0` for the pattern `*`. This is detected before any file is opened,
so no file is read and standard output stays empty. Exit status 2.

### 4.4 Standard input

When `pygrep` reads standard input — because there were no `FILE` operands, or
because an operand was `-` — the name used in prefixes (§2.2), in `-l` output
(§2.5) and in error messages (§4.1) is the literal string:

```
(standard input)
```

This matches GNU `grep`. With zero operands no prefix is printed at all, so the
name is visible only under `-l`:

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
| `0` | At least one line was selected, in at least one file. |
| `1` | No line was selected anywhere, and no error occurred. |
| `2` | An error occurred. |

The rules, in order of precedence:

1. If any usage error (§1.6) or invalid-pattern error (§4.3) occurred, the
   status is **2**.
2. Otherwise, if any file operand produced a per-file error (§4.1), the status
   is **2** — **even if other files produced matches, and even if output was
   written to standard output.** Verified against GNU `grep`:
   `grep beta a.txt nope.txt` prints `a.txt:beta` and exits 2.
3. Otherwise, if the total number of selected lines across all files is
   greater than zero, the status is **0**.
4. Otherwise the status is **1**.

Notes that follow from these rules:

- Under `-v`, "selected" means "non-matching", so `pygrep -v "" a.txt` exits 1.
- Under `-c`, printing `0` still means nothing was selected: `pygrep -c zzz
  a.txt` prints `0` and exits **1**.
- Under `-l`, the status is 0 if and only if at least one filename was printed.
- `-h`/`--help` exits **0**.
- An empty file, or a file with no matches, is not an error and never by itself
  causes status 2.

---

## 6. Test cases

Fixtures used below. Contents are given as Python string literals so that
newlines are unambiguous.

| File | Contents |
| --- | --- |
| `a.txt` | `"alpha\nbeta\nAlpha\ngamma\n"` |
| `b.txt` | `"beta\ndelta\n"` |
| `empty.txt` | `""` (zero bytes) |
| `nonl.txt` | `"no newline at end"` (no trailing newline) |
| `adir/` | a directory, empty |
| `nope.txt` | does not exist |

In the expectations, `""` means the stream is empty (zero bytes). Every
non-empty stdout shown ends with a newline.

---

**Test 1 — plain match, one file**
- given: `a.txt`
- run: `pygrep beta a.txt`
- expect: stdout `"beta\n"` · stderr `""` · exit `0`

**Test 2 — no match, one file**
- given: `a.txt`
- run: `pygrep zzz a.txt`
- expect: stdout `""` · stderr `""` · exit `1`

**Test 3 — filename prefix appears with two files**
- given: `a.txt`, `b.txt`
- run: `pygrep beta a.txt b.txt`
- expect: stdout `"a.txt:beta\nb.txt:beta\n"` · stderr `""` · exit `0`

**Test 4 — line numbers, one file (no prefix)**
- given: `a.txt`
- run: `pygrep -n beta a.txt`
- expect: stdout `"2:beta\n"` · stderr `""` · exit `0`

**Test 5 — line numbers restart per file, prefix present**
- given: `a.txt`, `b.txt`
- run: `pygrep -n beta a.txt b.txt`
- expect: stdout `"a.txt:2:beta\nb.txt:1:beta\n"` · stderr `""` · exit `0`

**Test 6 — `-c` with `-n`: `-n` is ignored**
- given: `a.txt`, `b.txt`
- run: `pygrep -c -n beta a.txt b.txt`
- expect: stdout `"a.txt:1\nb.txt:1\n"` · stderr `""` · exit `0`

**Test 7 — `-l` beats `-c`, in either order**
- given: `a.txt`, `b.txt`
- run: `pygrep -c -l beta a.txt b.txt`
- expect: stdout `"a.txt\nb.txt\n"` · stderr `""` · exit `0`
- run: `pygrep -l -c beta a.txt b.txt`
- expect: identical to the above

**Test 8 — `-c` prints 0 but the exit status is 1**
- given: `empty.txt`
- run: `pygrep -c anything empty.txt`
- expect: stdout `"0\n"` · stderr `""` · exit `1`

**Test 9 — empty pattern matches every line**
- given: `a.txt`
- run: `pygrep -c "" a.txt`
- expect: stdout `"4\n"` · stderr `""` · exit `0`

**Test 10 — empty pattern inverted selects nothing**
- given: `a.txt`
- run: `pygrep -v "" a.txt`
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
- given: `a.txt`
- run: `pygrep beta a.txt nope.txt`
- expect: stdout `"a.txt:beta\n"` · stderr `"pygrep: nope.txt: No such file or
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
- given: `a.txt`
- run: `pygrep -i alpha a.txt`
- expect: stdout `"alpha\nAlpha\n"` · stderr `""` · exit `0`

**Test 19 — invert with count**
- given: `a.txt`
- run: `pygrep -vc beta a.txt`
- expect: stdout `"3\n"` · stderr `""` · exit `0`

**Test 20 — `--` lets a pattern start with a dash**
- given: `dash.txt` containing `"has -x here\n"`
- run: `pygrep -- -x dash.txt`
- expect: stdout `"has -x here\n"` · stderr `""` · exit `0`

**Test 21 — invalid pattern is rejected before any file is read**
- given: `a.txt`
- run: `pygrep "*" a.txt`
- expect: stdout `""` · stderr matches `"pygrep: invalid pattern: "` followed
  by a nonempty detail, then `\n` · exit `2`

**Test 22 — `-l` prints the name even for a single file operand**
- given: `a.txt`
- run: `pygrep -l beta a.txt`
- expect: stdout `"a.txt\n"` · stderr `""` · exit `0`
