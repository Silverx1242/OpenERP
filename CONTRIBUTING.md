# Contribution Guide

Thank you for your interest in contributing to OpenERP!

## How to Contribute

### Reporting Bugs

If you find a bug, please:

1. Check that there isn't already an open issue reporting the same problem
2. Create a new issue with:
   - Clear description of the problem
   - Steps to reproduce
   - Expected behavior vs actual behavior
   - System information (OS, Python version, etc.)

### Suggesting Improvements

Suggestions for new features are welcome:

1. Open an issue with the "feature request" label
2. Clearly describe the proposed functionality
3. Explain why it would be useful for users

### Contributing Code

1. **Fork the repository**
2. **Create a branch** for your feature or fix:
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. **Make your changes** following the project conventions
4. **Test your changes** locally
5. **Commit** with descriptive messages:
   ```bash
   git commit -m "Add: description of changes"
   ```
6. **Push** to your fork:
   ```bash
   git push origin feature/my-new-feature
   ```
7. **Open a Pull Request** with a clear description of the changes

### Code Conventions

- Use descriptive names for variables and functions
- Add comments when code is not obvious
- Follow existing code style (PEP 8 for Python)
- Make sure code works on Windows, macOS and Linux

### Project Structure

- `app/` - Main application modules
  - `database.py` - Database management
  - `excel_export.py` - Excel export
  - `ui/` - Web interface (HTML/CSS/JS)
- `assets/` - Static resources (icons, etc.)
- `main.py` - Main entry point

## Questions

If you have questions, open an issue or contact the maintainers.

Thank you for helping improve OpenERP!
