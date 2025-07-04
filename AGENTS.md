# Guidance for AI Contributors

This project uses automated goals and compressed developer notes to coordinate development.

- **Goals** are listed in `GOALS.txt`. Keep this file up to date when objectives change.
- **Developer notes** are stored in `DEV_NOTES.dat` using a custom RLE+zlib compression format. Use `python3 dev_notes/notes_manager.py --show <id>` to view or `--add` to append notes. The tool handles compression and context-aware recompression automatically.
- Before sending a pull request or when beginning work, read both the goals and the decompressed notes to understand current priorities.
- After modifying code, always run `pytest -q` to ensure all tests pass.
- Follow basic Python style: 4-space indents and descriptive names. Avoid trailing whitespace.

These instructions apply repository-wide.
