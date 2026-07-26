# Testing Standards

## Test Structure
- Use pytest as test framework
- Follow Arrange-Act-Assert pattern
- Use descriptive test names (test_<what>_<condition>_<expected>)
- One assertion per test (prefer multiple tests over multiple assertions)

## Test Coverage
- Aim for 80%+ coverage on business logic
- 100% coverage on security-critical code
- Use pytest-cov for coverage reports

## Test Markers
- `@pytest.mark.asyncio` for async tests
- `@pytest.mark.slow` for long-running tests
- `@pytest.mark.integration` for external service tests

## Mocking
- Use unittest.mock for mocking
- Mock external services (APIs, databases)
- Use fixtures for common test data
