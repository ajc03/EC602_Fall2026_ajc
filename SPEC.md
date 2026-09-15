# Specifications for pygrep
**By AJ Chiaravalloti**

`pygrep` reads lines from a file and prints the lines that include a given string. It includes the arguments:

- `PATTERN` - The fixed string. If this string matches with any particular point of a line, that lines is printed.

- `FILE ..` - The number of files to search. If this is not specified, `pygrep` will only read one file.

- `-i` - This will cause `pygrep` to ignore letter case when matching strings.

- `-v` - Will select the lines that do *NOT* match instead of the lines that do match.

- `-n` - Will cause `pygrep` to include the line number as a prefix of each printed line

- `-c` - Will print only the count of selected lines for each file, instead of the lines themselves.
  - Can be used with `-i` to ignore letter case, and with `-v` to count the lines that do *NOT* match. Can *NOT* be used with `-n`. Only output will be 

- `-l` - Only prints the name of the files that have at least one relevant line.
  - Supersedes `-c`, `-n`, and `-v`, but can be used with `-i` to ignore letter case. If there is only one relevant file
