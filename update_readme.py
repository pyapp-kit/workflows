import yaml
from pathlib import Path
from rich import print

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


# Create markdown table
pyrepo_inputs = pyrepo["on"]["workflow_call"]["inputs"]
pyrepo_table = _input_table(pyrepo_inputs)
# update the readme
readme_lines = README.read_text().splitlines()
readme = "\n".join(readme_lines[: readme_lines.index("<!-- pyrepo-table -->") + 1])
readme += "\n" + pyrepo_table + "\n"
readme += "\n".join(readme_lines[readme_lines.index("<!-- /pyrepo-table -->") :])
README.write_text(readme)

deps_inputs = deps["on"]["workflow_call"]["inputs"]
deps_table = _input_table(deps_inputs)
# update the readme
readme_lines = README.read_text().splitlines()
readme = "\n".join(readme_lines[: readme_lines.index("<!-- deps-table -->") + 1])
readme += "\n" + deps_table + "\n"
readme += "\n".join(readme_lines[readme_lines.index("<!-- /deps-table -->") :])
README.write_text(readme)
