# Code Style Guide

## Python Style (PEP 8)

###Indentation
- 4 spaces per indentation level
- Never mix tabs and spaces

### Line Length
- Maximum 88 characters (ruff default)
- Break long lines at operators or commas

### Imports
- One import per line
- Group imports: stdlib → third-party → local
- Separate groups with blank lines

### Naming Conventions
- Functions: `snake_case`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private: `_leading_underscore`

### String Quotes
- Use double quotes for strings
- Use single quotes for dictionary keys

## Type Hints

### Function Signatures
```python
def process_data(data: list[str], count: int) -> dict[str, int]: ...
```

### Variables
```python
name: str = "John"
age: int = 25
items: list[str] = []
```

### Optional Types
```python
from typing import Optional


def find_user(user_id: int) -> Optional[User]: ...
```

## Docstrings

### Google Style
```python
def calculate_sum(numbers: list[int]) -> int:
    """Calculate the sum of a list of numbers.

    Args:
        numbers: List of integers to sum.

    Returns:
        The sum of all numbers.

    Raises:
        ValueError: If the list is empty.
    """
    ...
```

## Async Patterns

### Handler Functions
```python
async def handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle incoming update."""
    await update.message.reply_text("Response")
```

### Error Handling
```python
try:
    result = await some_operation()
except Exception as e:
    logger.error(f"Error: {e}")
    raise
```
