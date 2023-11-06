import yaml
from pathlib import Path

WORKFLOWS = Path(__file__).parent / ".github" / "workflows"
PYREPO = WORKFLOWS / "test-pyrepo.yml"
DEPS = WORKFLOWS / "test-dependents.yml"
README = Path(__file__).parent / "README.md"

pyrepo = yaml.safe_load(PYREPO.read_text().replace("\non:", '\n"on":'))
deps = yaml.safe_load(DEPS.read_text().replace("\non:", '\n"on":'))


def _input_table(inputs: dict) -> str:
    lines = ["| Input | Type | Default | Description |", "| --- | --- | --- | --- |"]
    for k, v in inputs.items():
        lines.append(
            f"| {k} | {v.get('type', '')} | "
            f"{v.get('default', '')!r} | {v.get('description', '')} |"
        )
    return "\n".join(lines)


def update_table(data: dict, key: str, readme_file: Path = README):
    # Create markdown table
    inputs = data["on"]["workflow_call"]["inputs"]
    table = _input_table(inputs)
    # update the readme
    readme_lines = readme_file.read_text().splitlines()
    readme = "\n".join(readme_lines[: readme_lines.index(f"<!-- {key} -->") + 1])
    readme += "\n" + table + "\n"
    readme += "\n".join(readme_lines[readme_lines.index(f"<!-- /{key} -->") :])
    readme_file.write_text(readme + "\n")


def main():
    update_table(pyrepo, "pyrepo-table")
    update_table(deps, "deps-table")

if __name__ == "__main__":
    main()