# Contributing to Kermi Modbus

Thank you for your interest in contributing to Kermi Modbus! This document provides guidelines and instructions for contributing.

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment for everyone.

## How to Contribute

### Reporting Bugs

1. **Check existing issues** to see if the bug has already been reported
2. **Create a detailed bug report** using the bug report template
3. Include:
   - Clear description of the bug
   - Steps to reproduce
   - Expected vs actual behavior
   - Environment details (OS, Python version, etc.)
   - Code example that reproduces the issue

### Suggesting Features

1. **Check existing feature requests** to avoid duplicates
2. **Create a feature request** using the feature request template
3. Include:
   - Clear description of the feature
   - Use cases and benefits
   - Example API usage
   - Any alternatives you've considered

### Pull Requests

#### Before Starting

1. **Open an issue first** to discuss major changes
2. **Fork the repository** and create a branch from `main`
3. **Set up your development environment**

#### Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/py-kermi-xcenter.git
cd py-kermi-xcenter

# Create a virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode with all dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

#### Making Changes

1. **Create a feature branch**:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Write your code** following our style guidelines:
   - Use Python 3.12+ features
   - Add type hints to all functions
   - Write docstrings (Google style)
   - Follow async/await patterns for I/O operations
   - Use explicit `get_*()` and `set_*()` methods

3. **Add tests** for your changes:
   - Add unit tests in `tests/`
   - Aim for >80% code coverage
   - Use pytest and pytest-asyncio
   - Mock external dependencies

4. **Run quality checks**:
   ```bash
   # Format code
   black src/ tests/ examples/

   # Lint code
   ruff check src/ tests/ examples/

   # Type check
   mypy src/

   # Run tests
   pytest -v --cov=kermi_xcenter
   ```

5. **Commit your changes**:
   - Write clear, descriptive commit messages
   - Reference issue numbers in commits
   - Keep commits focused and atomic

6. **Push and create a pull request**:
   ```bash
   git push origin feature/your-feature-name
   ```

#### Pull Request Guidelines

- **Title**: Clear and descriptive
- **Description**: Use the PR template
- **Tests**: All tests must pass
- **Coverage**: Don't decrease test coverage
- **Documentation**: Update docs if needed
- **Changelog**: Update if applicable

## Code Style

### Python Style

- **Formatter**: Black (line length: 100)
- **Linter**: Ruff
- **Type checker**: mypy (strict mode)
- **Docstrings**: Google style

### Naming Conventions

- **Classes**: `PascalCase` (e.g., `HeatPump`, `KermiModbusClient`)
- **Functions/Methods**: `snake_case` (e.g., `get_outdoor_temperature()`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `HEAT_PUMP_REGISTERS`)
- **Private**: Prefix with `_` (e.g., `_read_register()`)

### Code Organization

- **English names** throughout the codebase
- **German references** in docstrings for Kermi documentation
- **Type hints** on all public APIs
- **Async methods** for all I/O operations
- **Explicit getters/setters** rather than properties for I/O

### Example Code

```python
async def get_outdoor_temperature(self) -> float:
    """Get outdoor temperature in °C.

    Kermi code: BOT, Register: 3
    German: Außentemperaturfühler

    Returns:
        Temperature in degrees Celsius

    Raises:
        RegisterReadError: If read operation fails
    """
    return await self._read_register(self.registers["outdoor_temperature"])  # type: ignore
```

## Testing

### Writing Tests

- Use `pytest` and `pytest-asyncio`
- Mock external dependencies (pymodbus)
- Test both success and error cases
- Use descriptive test names

### Test Organization

```python
class TestHeatPumpTemperatures:
    """Test heat pump temperature readings."""

    @pytest.mark.asyncio
    async def test_get_outdoor_temperature(self, kermi_client, mock_tcp_client, mock_modbus_response):
        """Test reading outdoor temperature."""
        mock_tcp_client.read_holding_registers.return_value = mock_modbus_response([235])

        heat_pump = HeatPump(kermi_client)
        temp = await heat_pump.get_outdoor_temperature()

        assert temp == 23.5
```

### Running Tests

```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_heat_pump.py -v

# Run with coverage
pytest --cov=kermi_xcenter --cov-report=html

# Run specific test
pytest tests/test_heat_pump.py::TestHeatPumpTemperatures::test_get_outdoor_temperature -v
```

## Documentation

### Updating Documentation

- **Docstrings**: Add/update for all public APIs
- **README**: Update if adding major features
- **Examples**: Add examples for new features
- **Modbus Spec**: Update if adding new registers

### Documentation Style

- Clear and concise
- Include code examples
- Mention German equivalents from Kermi docs
- Include register addresses and Kermi codes

## Release Process

Releases are automated through GitHub Actions:

1. **Update version** in `pyproject.toml` and `src/kermi_xcenter/__init__.py`
2. **Update CHANGELOG.md** with release notes
3. **Create a git tag**: `git tag v0.1.0`
4. **Push tag**: `git push origin v0.1.0`
5. **Create GitHub release** - workflow will publish to PyPI automatically

## Questions?

- **GitHub Issues**: For bugs and features
- **GitHub Discussions**: For questions and help
- **Email**: Contact maintainers for sensitive issues

## License

By contributing, you agree that your contributions will be licensed under the Apache License 2.0.

## Recognition

All contributors will be recognized in the project README and release notes.

Thank you for contributing! 🎉
