---
description: Create a git commit with a descriptive message. Use when committing changes to the repository.
disable-model-invocation: true
allowed-tools: Bash(git add *) Bash(git commit *) Bash(git status *) Bash(git diff *)
---

## What I do

- Stage and commit current changes
- Generate descriptive commit messages
- Follow conventional commit format

## When to use me

Use this skill when you want to commit your changes with a proper commit message.

## Commit Process

1. Check current status: `git status`
2. Review changes: `git diff`
3. Stage changes: `git add .`
4. Commit with descriptive message

## Commit Message Format

```
<type>: <description>

[optional body]

[optional footer]
```

### Types

- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, missing semi-colons, etc)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

### Examples

```
feat: add user authentication handler
fix: resolve webhook signature validation issue
docs: update security audit chapter
refactor: improve error handling patterns
```

## Process

1. Run `git status` to see changed files
2. Run `git diff` to review changes
3. Run `git add .` to stage all changes
4. Run `git commit -m "type: description"` with appropriate message
5. Verify commit with `git log --oneline -5`
