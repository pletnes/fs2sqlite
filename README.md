# fs2sqlite

Getting an overview of a directory tree with many files can be daunting. The script
`fs2sqlite.py` lists recursively all files and directories, from the current
working directory, in a sqlite3 database called `files.db`.
To analyze the resulting database, the [datasette](https://datasette.io/)
package can be used for convenience.


## Usage

To run the script, simply run it as follows - there are no dependencies.

```bash
python fs2sqlite.py
```

If you want to analyze your filesystem with `datasette`,
[install](https://docs.datasette.io/en/stable/installation.html#using-pip) and
run as follows.  As an example, try to
[facet](https://docs.datasette.io/en/stable/facets.html) your files by file
suffix, then sort by file size.

```bash
pip install datasette
datasette serve --open files.db
```
