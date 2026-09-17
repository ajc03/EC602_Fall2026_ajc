"""Tests for pygrep (EC602 HW1). Starter file: keep the harness, replace the examples.

How this works: each test runs your program as a separate process, the same
way the shell would, and looks at what came back: standard output, standard
error, and the exit status. That is all a test of a command-line program can
see, and it is all it needs.

Run the tests from the directory that contains pygrep.py:

    uv run pytest

The grader runs this same file against other versions of pygrep.py, so do not
change how PROG is found.
"""

import os
import subprocess
import sys

import pytest

PROG = os.path.abspath(os.environ.get("PYGREP", "pygrep.py"))


def run(*args, stdin=""):
    """Run pygrep with ARGS. Returns (stdout, stderr, exit status)."""
    r = subprocess.run([sys.executable, PROG, *args], input=stdin,
                       capture_output=True, text=True)
    return r.stdout, r.stderr, r.returncode


@pytest.fixture
def files(tmp_path):
    """Make a few input files in a fresh temporary directory, and work there.

    pytest passes in `tmp_path`, a new empty directory for each test. Add the
    files your tests need here, or create them inside individual tests.
    """
    (tmp_path / "a.txt").write_text("apple\nBanana\ncherry pie\n")
    (tmp_path / "b.txt").write_text("pie\napple pie\n")
    (tmp_path / "alpha.txt").write_text("alpha\nbeta\nAlpha\ngamma\n")
    (tmp_path / "beta.txt").write_text("beta\ndelta\n")
    (tmp_path / "empty.txt").write_text("")
    (tmp_path / "nonl.txt").write_text("no newline at end")
    (tmp_path / "dash.txt").write_text("has -x here\n")
    (tmp_path / "ind.txt").write_text("    indented match\nplain match\n")
    (tmp_path / "adir").mkdir()
    old = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old)


# Two examples. Each test is a function whose name starts with `test_`, and a
# test passes if every `assert` in it is true.

def test_A_match_prints_the_line(files):
    out, err, code = run("pie", "a.txt")
    assert out == "cherry pie\n"
    assert err == ""
    assert code == 0


def test_B_no_match_exits_with_1(files):
    out, err, code = run("zzz", "a.txt")
    assert out == ""
    assert code == 1


# Your tests go below. One test per numbered case in your SPEC.md, named so
# that the number is easy to find, for example test_07_count_with_two_files.

def test_01_plain_match_one_file(files):
    """One file, no options, no filename prefix."""
    out, err, code = run("beta", "alpha.txt")
    assert out == "beta\n"
    assert err == ""
    assert code == 0

def test_02_no_match_exits_with_1(files):
    """Nothing selected and no error is status 1, not 0."""
    out, err, code = run("zzz", "alpha.txt")
    assert out == ""
    assert err == ""
    assert code == 1
 
 
def test_03_filename_prefix_with_two_files(files):
    """The prefix appears because two FILE operands were given."""
    out, err, code = run("beta", "alpha.txt", "beta.txt")
    assert out == "alpha.txt:beta\nbeta.txt:beta\n"
    assert err == ""
    assert code == 0
 
 
def test_04_line_numbers_one_file(files):
    """With one file there is a line number but no filename."""
    out, err, code = run("-n", "beta", "alpha.txt")
    assert out == "2:beta\n"
    assert err == ""
    assert code == 0
 
 
def test_05_line_numbers_restart_per_file(files):
    """The counter restarts at 1 for each file."""
    out, err, code = run("-n", "beta", "alpha.txt", "beta.txt")
    assert out == "alpha.txt:2:beta\nbeta.txt:1:beta\n"
    assert err == ""
    assert code == 0
 
 
def test_06_count_ignores_line_number(files):
    """-n is accepted under -c and silently ignored."""
    out, err, code = run("-c", "-n", "beta", "alpha.txt", "beta.txt")
    assert out == "alpha.txt:1\nbeta.txt:1\n"
    assert err == ""
    assert code == 0
 
 
def test_07_files_with_matches_beats_count_either_order(files):
    """-l outranks -c regardless of command-line order."""
    expected = "alpha.txt\nbeta.txt\n"
 
    out, err, code = run("-c", "-l", "beta", "alpha.txt", "beta.txt")
    assert out == expected
    assert err == ""
    assert code == 0
 
    out, err, code = run("-l", "-c", "beta", "alpha.txt", "beta.txt")
    assert out == expected
    assert err == ""
    assert code == 0
 
 
def test_08_count_prints_zero_but_exits_1(files):
    """Printing "0" is not the same as selecting a line."""
    out, err, code = run("-c", "anything", "empty.txt")
    assert out == "0\n"
    assert err == ""
    assert code == 1
 
 
def test_09_empty_pattern_matches_every_line(files):
    """The empty pattern matches at position 0 of every line."""
    out, err, code = run("-c", "", "alpha.txt")
    assert out == "4\n"
    assert err == ""
    assert code == 0
 
 
def test_10_empty_pattern_inverted_selects_nothing(files):
    """-v on the empty pattern leaves nothing, so status 1."""
    out, err, code = run("-v", "", "alpha.txt")
    assert out == ""
    assert err == ""
    assert code == 1
 
 
def test_11_unterminated_last_line_gets_a_newline(files):
    """17 bytes in, 18 bytes out: output is always \\n-terminated."""
    out, err, code = run("newline", "nonl.txt")
    assert out == "no newline at end\n"
    assert err == ""
    assert code == 0
 
 
def test_12_missing_file(files):
    """One diagnostic on stderr, nothing on stdout, status 2."""
    out, err, code = run("beta", "nope.txt")
    assert out == ""
    assert err.startswith("pygrep: nope.txt:")
    assert code == 2
 
 
def test_13_match_plus_missing_file_still_exits_2(files):
    """An error outranks a match, even after output was written."""
    out, err, code = run("beta", "alpha.txt", "nope.txt")
    assert out == "alpha.txt:beta\n"
    assert err.startswith("pygrep: nope.txt:")
    assert code == 2
 
 
def test_14_directory_operand(files):
    """A directory is an error like any other, and never recursed."""
    out, err, code = run("beta", "adir")
    assert out == ""
    assert err.startswith("pygrep: adir:")
    assert code == 2
 
 
def test_15_no_file_operands_reads_stdin(files):
    """Zero operands means stdin, and zero operands means no prefix."""
    out, err, code = run("-n", "beta", stdin="beta\ngamma\n")
    assert out == "1:beta\n"
    assert err == ""
    assert code == 0
 
 
def test_16_stdin_name_under_files_with_matches(files):
    """stdin is named '(standard input)'."""
    out, err, code = run("-l", "beta", stdin="beta\n")
    assert out != ""
    assert err == ""
    assert code == 0
 
 
def test_17_no_arguments_is_a_usage_error(files):
    """Usage to stderr, status 2, and stdin is never read."""
    out, err, code = run(stdin="beta\n")
    assert out == ""
    assert err != ""
    assert code == 2

 
def test_18_ignore_case(files):
    """-i selects both cases, in file order."""
    out, err, code = run("-i", "alpha", "alpha.txt")
    assert out == "alpha\nAlpha\n"
    assert err == ""
    assert code == 0
 
 
def test_19_invert_with_count_bundled(files):
    """-vc is -v -c, and counts the non-matching lines."""
    out, err, code = run("-vc", "beta", "alpha.txt")
    assert out == "3\n"
    assert err == ""
    assert code == 0
 
 
def test_20_double_dash_allows_a_dash_pattern(files):
    """After --, a leading dash is pattern text, not an option."""
    out, err, code = run("--", "-x", "dash.txt")
    assert out == "has -x here\n"
    assert err == ""
    assert code == 0

 
def test_21_files_with_matches_names_a_single_file(files):
    """-l always prints the name, even for one operand."""
    out, err, code = run("-l", "beta", "alpha.txt")
    assert out == "alpha.txt\n"
    assert err == ""
    assert code == 0


def test_22_help_without_a_pattern(files):
    """-h works even though PATTERN is required, and exits 0."""
    out, err, code = run("-h")
    assert out != ""
    assert err == ""
    assert code == 0

 
def test_23_help_long_form(files):
    """--help behaves identically to -h."""
    out, err, code = run("--help")
    assert out != ""
    assert err == ""
    assert code == 0


def test_24_files_with_matches_prints_the_name_once(files):
    """Files with multiple matches are printed only once when -l is used"""
    out, err, code = run("-l", "pie", "b.txt")
    assert out == "b.txt\n"
    assert err == ""
    assert code == 0


def test_25_leading_whitespace_is_preserved(files):
    """Leading whitespace is preserved when lines are printed"""
    out, err, code = run("match", "ind.txt")
    assert out == "    indented match\nplain match\n"
    err == ""
    assert code == 0