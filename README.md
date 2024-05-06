# Reusable workflows

This repo contains a set of reusable workflows for use in GitHub Actions.

They are used by repos in the pyapp-kit organization, but you may use them
as well if you find them useful for your own projects.

1. [test-pyrepo.yml](#run-python-tests) - use to run tests for your python package
2. [test-dependents.yml](#test-dependent-packages) - use to test that updates to your
   package don't break another package that depends on your package

## Run python tests

[`uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@v2`](.github/workflows/test-pyrepo.yml)

Standard workflow to setup python and test a python package, in the following order:

1. Checks out the repo using [`actions/checkout`](https://github.com/actions/checkout) with `inputs.fetch-depth`
2. Runs [`actions/setup-python`](https://github.com/actions/setup-python) with `python-version`
3. If `inputs.qt != ''`: Installs Qt libs using [tlambert03/setup-qt-libs](https://github.comtlambert03/setup-qt-libs)
4. Installs dependencies using `pip install .[extras]`
5. Runs `pytest --cov --cov-report=xml inputs.pytest-args` unless overridden.
   - If `inputs.qt != ''`: Runs headlessly using [`aganders3/headless-gui`](https://github.com/actions/aganders3/headless-gui)
6. Uploads coverage reports using [`codecov/codecov-action`](https://github.com/codecov/codecov-action)
7. If `report-failures != ''` Opens an issue to report failures.  Useful for cron jobs for pre-release testing.

### Inputs

(All inputs are optional)

<!-- pyrepo-table -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| python-version | string | 3.x | Python version to use. Passed to `actions/setup-python`. |
| os | string | ubuntu-latest | Operating system to use. Passed to `runs-on:`. |
| extras | string | test | Package extras to install (may use commas for multiples `'test,docs'`). If you don't have an extra named 'test' you should change this. |
| pip-install-flags | string |  | Additional flags to pass to pip install. Can be used for `--editable`, `--no-deps`, etc. |
| pip-install-pre-release | boolean | False | Whether to install pre-releases in the pip install phase with `--pre`. |
| pip-install-min-reqs | boolean | False | Whether to install the *minimum* declared dependency versions. |
| pip-pre-installs | string |  | Packages to install *before* calling `pip install .` |
| pip-post-installs | string |  | Packages to install *after* `pip install .`. (these are called with `--force-reinstall`.) |
| qt | string |  | Version of qt to install (or none if blank). Will also install qt-libs and run tests headlessly if not blank. |
| fetch-depth | number | 1 | The number of commits to fetch. 0 indicates all history for all branches and tags. |
| python-cache-dependency-path | string | pyproject.toml | passed to `actions/setup-python` |
| pytest-args | string |  | Additional arguments to pass to pytest. Can be used to specify paths or for for `-k`, `-x`, etc. |
| fail-on-coverage-error | boolean | True | Fail the build if codecov action fails. |
| hatch-build-hooks-enable | boolean | False | Value for [`HATCH_BUILD_HOOKS_ENABLE`](https://hatch.pypa.io/latest/config/build/#environment-variables). |
| report-failures | string |  | (true or false). Whether to create a GitHub issue when a test fails. If not set, will be true for scheduled runs, and false otherwise. |
| cache-key | string |  | Cache key to use for caching. If not set, no caching will be used. |
| cache-path | string |  | Path to cache. If not set, no caching will be used. |
| cache-script | string |  | Script to run to create the cache. If not set, no caching will be used. |
| coverage-upload | string | codecov | How to upload coverage data. Options are `'artifact'`, `'codecov'`. If using 'artifact', coverage must be sent to codecov in a separate workflow. (*see upload-coverage.yml*) |

**Secrets:**

| Input | Description |
| --- | --- |
| codecov_token | Token for codecov-action. Only used if `pytest-cov-flags` is not empty and coverage-upload is 'codecov'. |
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
    uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@v2
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

Note that the default value for `report-failures` is `${{ github.event_name == 'schedule' }}`, so you don't need to specify it unless you want to override the
default.  However, you may wish to use
`pip-install-pre-release: ${{ github.event_name == 'schedule' }}`
to test pre-release versions when triggered by a cron job.

```yaml
name: CI

on:
  schedule:
    - cron: "0 0 * * *"

jobs:
  run_tests:
    uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@v2
    with:
      os: ${{ matrix.os }}
      python-version: ${{ matrix.python-version }}
      # Test pre-release versions when triggered by a schedule
      # and open an issue if the tests fail
      pip-install-pre-release: ${{ github.event_name == 'schedule' }}
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
    uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@v2
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

#### Separate codecov reporting into a separate job

Because codecov can often fail, you might want to combine all
reports and upload in a single step.  For this, change the
`coverage-upload` input to `artifact` and add a separate job
to upload the coverage report using [`upload-coverage.yml`](#combine-and-upload-coverage-artifacts).

```yaml
name: CI

jobs:
  tests:
    uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@v2
    with:
      os: ${{ matrix.os }}
      python-version: ${{ matrix.python-version }}
      # changing this to "artifact" prevents uploading to codecov here,
      # instead it uploads an artifact with the coverage data
      coverage-upload: artifact
    strategy:
      fail-fast: false
      matrix:
        os: [ubuntu-latest, macos-latest, windows-latest]
        python-version: ["3.10", "3.11", "3.12"]

  # now add an additional job to combine and upload the coverage
  upload_coverage:
    if: always()
    needs: [tests]
    uses: pyapp-kit/workflows/.github/workflows/upload-coverage.yml@v2
    secrets:
      codecov_token: ${{ secrets.CODECOV_TOKEN }}
```

## Test Dependent Packages

[`uses: pyapp-kit/workflows/.github/workflows/test-dependents.yml@v2`](.github/workflows/test-dependents.yml)

This workflow is useful when your package is a dependency of other packages, and you
would like to ensure that your changes don't break those packages.

1. Checks out the "host" repo (the repo using this workflow) using [`actions/checkout`](https://github.com/actions/checkout).
2. Checks out `dependency-repo` @ `dependency-ref` using [`actions/checkout`](https://github.com/actions/checkout).
3. Runs [`actions/setup-python`](https://github.com/actions/setup-python) with `python-version`
4. If `inputs.qt != ''`: Installs Qt libs using [tlambert03/setup-qt-libs](https://github.comtlambert03/setup-qt-libs)
5. Installs dependencies for `dependency-repo` followed by the host repo.
6. Runs `pytest inputs.pytest-args` (add specific paths or `-k` flags here)
   - If `inputs.qt != ''`: Runs headlessly using [`aganders3/headless-gui`](https://github.com/actions/aganders3/headless-gui)

### Inputs

(Only `dependency-repo` is required)

<!-- deps-table -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| dependency-repo | string |  | Repository name with owner of package to test (org/repo). |
| dependency-ref | string |  | Ref to checkout in dependency-repo. Defaults to HEAD in default branch. |
| python-version | string | 3.x | Python version to use. Passed to `actions/setup-python`. |
| os | string | ubuntu-latest | Operating system to use. Passed to `runs-on:`. |
| host-extras | string |  | Extras to use when installing host (package running this workflow). |
| dependency-extras | string | test | Extras to use when installing dependency-repo. |
| qt | string |  | Version of Qt to install. |
| post-install-cmd | string |  | Command(s) to run after installing dependencies. |
| pytest-args | string |  | Additional arguments to pass to pytest. Can be used to specify paths or for for `-k`, `-x`, etc. |
<!-- /deps-table -->

### Example dependecy test

Here's an example where package Package B depends on Package A.

This workflow would go into Package A's repository, and tests that changes made to Package A don't break
Package B.

```yaml
name: CI

jobs:
  test-package-b:
    uses: pyapp-kit/workflows/.github/workflows/test-dependents.yml@v2
    with:
      os: ${{ matrix.os }}
      python-version: ${{ matrix.python-version }}
      dependency-repo: some-org/package-b
      dependency-ref: ${{ matrix.package-b-version }}
      dependency-extras: "test"  # Extras to use when installing dependency-repo.
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ["3.10", "3.12"]
        package-b-version: ["", "v0.5.0"]
```

## Combine and Upload Coverage Artifacts

[`uses: pyapp-kit/workflows/.github/workflows/upload-coverage.yml@v2`](.github/workflows/upload-coverage.yml)

This workflow is designed to be used in conjunction with the `test-pyrepo.yml` workflow
when the `coverage-upload` input is set to `artifact`.

<!-- coverage-table -->
| Input | Type | Default | Description |
| --- | --- | --- | --- |
| fail-on-coverage-error | boolean | True | Fail if codecov action fails. |
| artifact-pattern | string | covreport-* | glob pattern to the artifacts that should be downloaded for coverage reports. This should match the `name` you used for the `upload-artifact` step in the job that generates the coverage reports. (*This default matches the name in test-pyrepo.yml*) |

**Secrets:**

| Input | Description |
| --- | --- |
| codecov_token | Token for codecov-action. |
<!-- /coverage-table -->
