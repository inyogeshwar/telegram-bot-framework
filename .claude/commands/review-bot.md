# Review Bot Code

Reviews Telegram bot code for best practices, security, and performance.

## Instructions

1. Read the specified bot file(s)
2. Analyze against checklist:
   - Security vulnerabilities
   - Async/await patterns
   - Error handling
   - Type hints
   - Performance issues
   - Code quality

3. Generate review report with:
   - Critical issues (must fix)
   - Warnings (should fix)
   - Suggestions (nice to have)
   - Positive aspects

## Review Checklist

### Security
- [ ] No hardcoded tokens/secrets
- [ ] Input validation implemented
- [ ] Rate limiting considered
- [ ] Webhook validation (if applicable)
- [ ] Proper error messages (no info leakage)

### Async Patterns
- [ ] All handlers are async
- [ ] No blocking calls in handlers
- [ ] Proper await usage
- [ ] Database calls use async drivers

### Error Handling
- [ ] Global error handler registered
- [ ] Handler-specific error handling
- [ ] Logging configured
- [ ] Graceful degradation

### Type Hints
- [ ] Function parameters typed
- [ ] Return types specified
- [ ] Variables annotated where helpful
- [ ] Generic types used correctly

### Code Quality
- [ ] PEP 8 compliant
- [ ] No code duplication
- [ ] Clear function names
- [ ] Docstrings present
- [ ] Constants defined

### Performance
- [ ] Efficient database queries
- [ ] Connection pooling
- [ ] Caching considered
- [ ] Background tasks appropriate

## Output Format

```markdown
# Code Review: [bot_name.py]

## Summary
[Brief overview]

## Critical Issues
1. [Issue description]
   - Location: [file:line]
   - Impact: [security/stability/performance]
   - Fix: [suggested fix]

## Warnings
1. [Warning description]
   - Location: [file:line]
   - Recommendation: [suggestion]

## Suggestions
1. [Improvement idea]
   - Benefit: [why it's better]

## Positive Aspects
- [Things done well]

## Overall Score: [1-10]/10
```

## Resources
- Reference: .claude/rules/core.md
- Security: .claude/rules/security.md
- Testing: .claude/rules/testing.md
- Functions: docs/COMPREHENSIVE-REFERENCE.md
