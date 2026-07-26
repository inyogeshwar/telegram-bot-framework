---
description: Review code changes
agent: code-reviewer
subtask: true
---

Review the recent code changes.

!`git diff HEAD~5 --stat`

Review the actual changes:

!`git diff HEAD~5`

Focus on:
1. Code quality and best practices
2. Security vulnerabilities
3. Performance issues
4. Type hint completeness
5. Error handling
6. Documentation quality

Provide a summary with:
- Critical issues (must fix)
- Warnings (should fix)
- Suggestions (nice to have)
- Overall score (1-10)
