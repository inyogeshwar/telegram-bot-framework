# File-Specific Rules

## Python Files (*.py)
- Use double quotes for strings
- Use trailing commas in multi-line structures
- Imports: stdlib → third-party → local (separated by blank lines)
- Type hints on all function parameters and return values
- Use `|` for union types (Python 3.10+)
- Use `X | None` instead of `Optional[X]`

## Documentation Files (*.md)
- Use ATX-style headers (# , ## , ### )
- Max line length: 120 characters for prose
- Include code blocks with language specifiers
- Use relative links for internal references

## Configuration Files (*.json, *.yaml, *.toml)
- Validate JSON/YAML syntax
- Use consistent indentation (2 spaces for YAML, 4 for Python)
- No trailing commas in JSON
