# Contributing Guide

Thank you for your interest in contributing to **mapmetnet**! We welcome contributions from the community and are grateful for your support.

## Project Purpose
This library is developed primarily to support the operational, scientific, and research needs of MeteoSwiss. While the project is open source and welcomes external contributions, it is intended to be released, maintained, and distributed under the MeteoSwiss name. Contributions should align with this mission and the long‑term goals of the organization.

## Code of Conduct

This project adheres to the Contributor Covenant Code of Conduct. By participating, you are expected to uphold this code. Please read the full [Code of Conduct](CODE_OF_CONDUCT.md) before contributing.

## How Can I Contribute?

### Reporting Bugs

Bug reports should be submitted as [Github Issues](https://github.com/MeteoSwiss/mapmetnet/issues). Before submitting a new issue, please check existing issues to avoid duplicates. Please include as many details as possible.

### Suggesting Features

Feature suggestions are welcome. Please do so using our [feature request template](https://github.com/MeteoSwiss/mapmetnet/issues) to do so.


### Contributing Code

1. Fork the repository
2. Create a new branch for your feature or bugfix
3. Make your changes following our coding standards
4. Write or update tests as needed
5. Ensure all tests pass and code quality checks succeed
6. Submit a pull request

## Development Setup

### Prerequisites

- Python 3.11 or higher
- Git

### Setting Up Your Environment

1. Clone your fork of the repository:

   ```console
   $ git clone https://github.com/MeteoSwiss/mapmetnet.git
   $ cd mapmetnet
   ```

2. Install dependencies:

   ```console
   $ pip install -e .
   ```

3. Verify your setup by running the tests:

   ```console
   $ pytest
   ```

## Code Style and Quality

This project uses several tools to maintain code quality:

### Linting with Pylint

Run pylint to check for code quality issues:

```console
$ pylint src
```

The project configuration is in `pyproject.toml`. We disable certain docstring requirements but maintain other quality standards.

### Type Checking with Mypy

We enforce type hints throughout the codebase:

```console
$ mypy src
```

All function definitions must include type annotations.

## Testing Guidelines

### Writing Tests

- Write unit tests for all new code
- Place tests in the `test/` directory
- Follow the existing test structure and naming conventions
- Use descriptive test names that explain what is being tested
- Aim for high code coverage (check with `pytest-cov`)

### Running Tests

Run all tests with coverage:

```console
$ pytest --cov=src
```

## Documentation

- Add docstrings to new functions, classes, and modules
- Update documentation for any changed functionality
- For new pages: disable the html sidebar in ``conf.py``
- Follow the existing documentation style
- Build documentation locally to verify changes:

  ```console
  $ sphinx-build doc doc/_build
  ```

## Pull Request Process

1. **Update the CHANGELOG**: Add a brief description of your changes in **CHANGELOG**

2. **Update AUTHORS**: If this is your first contribution, add your name to the **AUTHORS** file

3. **Create a Pull Request**: Use our **pull request template** and ensure you:

   - Provide a clear description of the changes
   - Reference any related issues (e.g., "Closes #123")
   - Complete the checklist in the PR template
   - Ensure all CI checks pass

4. **Code Review**: A maintainer will review your PR. Be prepared to make changes based on feedback

5. **Merge**: Once approved and all checks pass, a maintainer will merge your PR

### Commit Messages

Write clear, concise commit messages:

- Use the imperative mood ("Add feature" not "Added feature")
- Start with a capital letter
- Keep the first line under 50 characters
- Add a blank line followed by a detailed description if needed

## License

By contributing to this project, you agree that your contributions will be licensed under the BSD-3-Clause License.

## Questions?

If you have questions about contributing, please:

- Check existing issues and discussions
- Review the documentation
- Create a new issue with your question

Thank you for contributing to mapmetnet!

## Release mechanism

The project follows the MeteoSwiss GitOps concept: releases are triggered whenever a Git TAG is created.

The TAG must follow the [semantic version](https://semver.org/) format and [PEP 440](https://peps.python.org/pep-0440/), otherwise the release task will fail.

Steps to follow for a new release:

* Adapt ``CHANGELOG.rst`` with release information
* Adapt ``doc/_static/switcher_config.json`` adding the new documentation URL for the release
* Create a new Release in the Github project
