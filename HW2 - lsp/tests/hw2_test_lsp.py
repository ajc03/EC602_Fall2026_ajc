"""Tests for lsp (EC602 HW2). Starter file: keep the harness, replace the examples.

How this works: each test runs the program as a separate process, the same way
the shell would, and looks at what came back: standard output, standard error,
and the exit status.

Run the tests from the directory that contains lsp.py:

    uv run pytest

The grader runs this same file against other versions of lsp.py, so do not
change how PROG is found.
"""

import os
import subprocess
import sys
import time

import pytest

PROG = os.path.abspath(os.environ.get("LSP", "hw2_lsp.py"))

# Every file in the fixture gets this modification time, so a test can say
# what the time column must contain. time.localtime, because that is what the
# specification says the column shows.
STAMP = 1_735_700_000
WHEN = time.strftime("%Y-%m-%d %H:%M", time.localtime(STAMP))


def run(*args):
    """Run lsp with ARGS. Returns (stdout, stderr, exit status)."""
    r = subprocess.run([sys.executable, PROG, *args], capture_output=True, text=True)
    return r.stdout, r.stderr, r.returncode


@pytest.fixture
def tree(tmp_path):
    """A directory with a known set of entries, and the current directory set to it.

    This is the directory that the test cases in SPEC.md are written against.
    Permissions and modification times are set explicitly, because a test of
    `-l` has to know what they are.
    """
    (tmp_path / "apple").write_text("hello")
    (tmp_path / "Banana").write_text("")
    (tmp_path / "notes.txt").write_text("a\nb\n")
    (tmp_path / ".hidden").write_text("x")
    (tmp_path / "sub").mkdir()
    for name in ("apple", "Banana", "notes.txt", ".hidden"):
        os.chmod(tmp_path / name, 0o644)
        os.utime(tmp_path / name, (STAMP, STAMP))
    os.chmod(tmp_path / "sub", 0o755)
    os.utime(tmp_path / "sub", (STAMP, STAMP))
    old = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(old)


# Two examples. Each test is a function whose name starts with `test_`, and a
# test passes if every `assert` in it is true.

def test_01_default_lists_visible_entries_in_code_point_order(tree):
    out, err, code = run()
    assert out == "Banana\napple\nnotes.txt\nsub\n"
    assert err == ""
    assert code == 0

def test_09_missing_path_is_reported_on_stderr(tree):
    out, err, code = run("nope")
    assert out == ""
    assert err == "lsp: nope: No such file or directory\n"
    assert code == 1

# Your tests go below: one per numbered case in SPEC.md, then your own.

# Previously numbered cases

def test_02_directory_argument(tree):
    out, err, code = run("sub")
    assert out == ""
    assert err == ""
    assert code == 0
    assert run(".") == run()

def test_03_dash_a(tree):
    out, err, code = run("-a")
    assert out == ".\n..\n.hidden\nBanana\napple\nnotes.txt\nsub\n"
    assert err == ""
    assert code == 0

def test_04_middle_dot(tree):
    out, err, code = run()
    names = out.splitlines()
    assert "notes.txt" in names
    assert ".hidden" not in names
    assert err == ""
    assert code == 0

def test_05_dash_r(tree):
    out, err, code = run("-r")
    assert out == "sub\nnotes.txt\napple\nBanana\n"
    assert err == ""
    assert code == 0

def test_06_dash_a_and_dash_r(tree):
    out, err, code = run("-a", "-r")
    assert out == "sub\nnotes.txt\napple\nBanana\n.hidden\n..\n.\n"
    assert err == ""
    assert code == 0

def test_07_long_format_files(tree):
    out, err, code = run("-l")
    lines = out.splitlines()
    assert lines[0] == "-rw-r--r--        0 " + WHEN + " Banana"
    assert lines[1] == "-rw-r--r--        5 " + WHEN + " apple"
    assert err == ""
    assert code == 0

def test_08_long_format_directory(tree):
    out, err, code = run("-l")
    lines = out.splitlines()
    assert len(lines) == 4
    assert lines[3].startswith("drwxr-xr-x" + " ")
    assert lines[3].endswith(" " + WHEN + " sub")
    assert err == ""
    assert code == 0

def test_10_file_as_the_argument(tree):
    out, err, code = run("apple")
    assert out == "apple\n"
    assert err == ""
    assert code == 0
    out, err, code = run("-l", "apple")
    assert out == "-rw-r--r--        5 " + WHEN + " apple\n"
    assert err == ""
    assert code == 0

def test_11_empty_directory(tree):
    out, err, code = run("sub")
    assert out == ""
    assert err == ""
    assert code == 0

def test_12_bad_option(tree):
    out, err, code = run("-z")
    assert out == ""
    assert "usage" in err
    assert code == 2

# New test cases

def test_A_options_together_and_apart(tree):
    assert run("-a", "-l") == run("-al")
    assert run("-a", "-l") == run("-la")
    assert run("-a", "-l") == run("-l", "-a")

def test_B_repeating_options(tree):
    assert run("-r") == run("-r", "-r")
    assert run("-a") == run("-a", "-a")

def test_C_long_help(tree):
    out, err, code = run("--help")
    assert "usage" in out
    assert err == ""
    assert code == 0

def test_D_dash_h_error(tree):
    out, err, code = run("-h")
    assert out == ""
    assert "usage" in err
    assert code == 2

def test_E_no_long_options(tree):
    out, err, code = run("--all")
    assert out == ""
    assert err != ""
    assert code == 2

def test_F_all_on_empty_directory(tree):
    out, err, code = run("-a", "sub")
    assert out == ".\n..\n"
    assert err == ""
    assert code == 0

def test_G_file_argument(tree):
    out, err, code = run("./apple")
    assert out == "./apple\n"
    assert err == ""
    assert code == 0

def test_H_all_and_reverse_effect(tree):
    out, err, code = run("-a", "-r", "apple")
    assert out == "apple\n"
    assert err == ""
    assert code == 0

def test_I_hidden_file_named(tree):
    out, err, code = run(".hidden")
    assert out == ".hidden\n"
    assert err == ""
    assert code == 0

def test_J_missing_path_reported(tree):
    out, err, code = run("./nope")
    assert out == ""
    assert err == "lsp: ./nope: No such file or directory\n"
    assert code == 1

def test_K_long_format_same_error(tree):
    out, err, code = run("-l", "nope")
    assert out == ""
    assert err == "lsp: nope: No such file or directory\n"
    assert code == 1

def test_L_two_paths(tree):
    out, err, code = run("apple", "sub")
    assert out == ""
    assert "usage" in err
    assert code == 2

# This section only exists because the original tests and what was described in SPEC.md did not test permissions.
@pytest.mark.skipif(hasattr(os, "geteuid") and os.geteuid() == 0,   # This is to make sure the locked file is actually tested, in case 0o000 can actually be read on another computer
                    reason="root can read any directory")
def test_M_permission_denied(tree):
    locked = tree / "locked"    # Create locked only in this test because I do not want to break all the other tests that require length or file location
    locked.mkdir()
    os.chmod(locked, 0o000)
    try:
        out, err, code = run("locked")
    finally:
        os.chmod(locked, 0o755)
    assert out == ""
    assert err == "lsp: locked: Permission denied\n"
    assert code == 1
