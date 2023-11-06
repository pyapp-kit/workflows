# Reusable workflows

This repo contains a set of reusable workflows for use in GitHub Actions.

They are used by repos in the pyapp-kit organization, but you may use them
as well if you find them useful for your own projects.

## Run python tests

[`uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@v1`](.github/workflows/test-pyrepo.yml)

Standard workflow to setup python and test a python package.

```yaml
    uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@v1
```

(All inputs are optional)

<!-- pyrepo-table -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| python-version | string | '3.x' | Python version to use. Passed to `actions/setup-python`. |
| os | string | 'ubuntu-latest' | Operating system to use. Passed to `runs-on:`. |
| extras | string | 'test' | Package extras to install (may use commas for multiples `'test,docs'`). If you don't have an extra named 'test' you should change this. |
| pip-install-flags | string | '' | Additional flags to pass to pip install. Can be used for `--editable`, `--no-deps`, etc. |
| pip-install-pre-release | boolean | False | Whether to install pre-releases in the pip install phase with `--pre` |
| pip-pre-installs | string | '' | Packages to install *before* calling `pip install .` |
| pip-post-installs | string | '' | Packages to install *after* `pip install .`. (these are called with `--force-reinstall`.) |
| qt | string | '' | Version of qt to install (or none if blank).  Will also install qt-libs and run tests headlessly if not blank. |
| fetch-depth | number | 1 | The number of commits to fetch. 0 indicates all history for all branches and tags. |
| python-cache-dependency-path | string | 'pyproject.toml' | passed to `actions/setup-python` |
| pytest-args | string | '' | Additional arguments to pass to pytest. Can be used to specify paths or for for `-k`, `-x`, etc. |
| pytest-cov-flags | string | '--cov --cov-report=xml --cov-report=term-missing' | Flags to pass to pytest-cov. Can be used for `--cov-fail-under`, `--cov-branch`, etc. Note: it's best to specify `[tool.coverage.run] source = ['your_package']`. |
| fail-on-coverage-error | boolean | True | Fail the build if codecov action fails. |
| hatch-build-hooks-enable | boolean | False | Value for [`HATCH_BUILD_HOOKS_ENABLE`](https://hatch.pypa.io/latest/config/build/#environment-variables). |
| report-failures | boolean | False | Whether to create a GitHub issue when a test fails. Good for cron jobs. |
<!-- /pyrepo-table -->

See complete up-to-date list of options in [`test-pyrepo.yml`](.github/workflows/test-pyrepo.yml#L5)

### Example usage

You can mix and match the inputs to suit your needs.  But here are
some common patterns.

#### General pattern

```yaml
name: CI

jobs:
  run_tests:
    uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@main
    with:
      os: ${{ matrix.os }}
      python-version: ${{ matrix.python-version }}
      extras: 'test'  # this is the default... but you can specify others
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]
```

#### Testing depenency pre-releases on a schedule

```yaml
name: CI

on:
  schedule:
    - cron: "0 0 * * *"

jobs:
  run_tests:
    uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@main
    with:
      os: ${{ matrix.os }}
      python-version: ${{ matrix.python-version }}
      # Test pre-release versions when triggered by a schedule
      # and open an issue if the tests fail
      pip-install-pre-release: ${{ github.event_name == 'schedule' }}
      report-failures: ${{ github.event_name == 'schedule' }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]
```

#### Testing things with Qt

Use the `qt` input to:

- install the specified Qt binding
- install libraries on linux using [tlambert03/setup-qt-libs](https://github.com/tlambert03/setup-qt-libs)
- run headless tests using [aganders3/headless-gui](https://github.com/aganders3/headless-gui)

```yaml
name: CI

jobs:
  run_tests:
    uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@main
    with:
      os: ${{ matrix.os }}
      python-version: ${{ matrix.python-version }}
      qt: ${{ matrix.qt }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]
        qt: ["", "PyQt6", "PySide6"]
```

## Test Dependent Packages

<!-- deps-table -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| package_to_test | string | '' | Repository name with owner of package to test (org/repo). |
| package_to_test_ref | string | '' | Ref to checkout in package to test. Defaults to default branch. |
| python-version | string | '3.x' |  |
| os | string | 'ubuntu-latest' |  |
| host-extras | string | '' | Extras to install for host repo. |
| package-extras | string | '' | Extras to install for package to test. |
| qt | string | '' | Version of Qt to install. |
| post_install_cmd | string | '' | Command to run after installing dependencies. |
| pytest-args | string | '' | Arguments to pass to pytest. |
<!-- /deps-table -->