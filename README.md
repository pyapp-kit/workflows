# Reusable workflows

### Run python tests

[`uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@main`](.github/workflows/test-pyrepo.yml)

Standard workflow to setup python and test a python package.

```yaml
    uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@main
```

See options in [`test-pyrepo.yml`](.github/workflows/test-pyrepo.yml#L5-L60)

<details>

<summary>Example usage</summary>

```yaml
name: CI

jobs:
  run_tests:
    uses: pyapp-kit/workflows/.github/workflows/test-pyrepo.yml@main
    with:
      os: ${{ matrix.os }}
      python-version: ${{ matrix.python-version }}
    strategy:
      fail-fast: false
      matrix:
        python-version: ["3.10", "3.11", "3.12"]
        os: [ubuntu-latest, macos-latest, windows-latest]
```

</details>
