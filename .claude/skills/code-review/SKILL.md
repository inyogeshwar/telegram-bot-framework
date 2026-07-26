---
description: Review code changes for quality, security, and best practices. Use when reviewing pull requests or checking code quality.
context: fork
agent: Explore
allowed-tools: Read Grep Glob
---

## What I do

- Review code for quality and best practices
- Check for security vulnerabilities
- Verify error handling and logging
- Ensure type hints and documentation

## When to use me

Use this skill when reviewing code changes, pull requests, or checking code quality.

## Review Checklist

### Code Quality
- [ ] Follows PEP 8 style guidelines
- [ ] Uses consistent naming conventions
- [ ] Has appropriate comments and docstrings
- [ ] Functions are not too long (max 50 lines)
- [ ] No unused imports or variables

### Type Safety
- [ ] All functions have type hints
- [ ] Return types are specified
- [ ] Optional types are used correctly
- [ ] No `Any` types unless necessary

### Error Handling
- [ ] All exceptions are caught appropriately
- [ ] Error messages are descriptive
- [ ] Logging is included
- [ ] Graceful degradation implemented

### Security
- [ ] No hardcoded tokens or secrets
- [ ] Input validation present
- [ ] Rate limiting considered
- [ ] Webhook signatures validated (if applicable)

### Telegram-Specific
- [ ] Uses async/await patterns
- [ ] Handler signatures correct
- [ ] Callback queries answered
- [ ] Context types properly annotated

## Review Process

1. Read the changed files
2. Check for code quality issues
3. Verify error handling
4. Review security implications
5. Provide constructive feedback

## Output Format

```markdown
## Code Review

### Strengths
- [list positives]

### Issues Found
- [list issues with severity]

### Recommendations
- [list suggestions]
```
