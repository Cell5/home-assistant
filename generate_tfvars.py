import argparse
import re
from pathlib import Path
from typing import Any

EXAMPLE_FILENAME = "terraform.tfvars.example"
OUTPUT_FILENAME = "terraform.tfvars"

VAR_PATTERN = re.compile(r'^\s*#\s*([a-zA-Z0-9_]+)\s*=\s*(.+)$')


def parse_example(example_path: Path) -> list[tuple[str, str, Any]]:
    variables = []
    for line in example_path.read_text(encoding="utf-8").splitlines():
        match = VAR_PATTERN.match(line)
        if not match:
            continue
        name, raw_value = match.groups()
        raw_value = raw_value.strip()
        if raw_value.startswith("[") and raw_value.endswith("]"):
            value_type = list
            default = raw_value
        elif raw_value.startswith('"') and raw_value.endswith('"'):
            value_type = str
            default = raw_value.strip('"')
        else:
            try:
                default = int(raw_value)
                value_type = int
            except ValueError:
                value_type = str
                default = raw_value.strip('"')
        variables.append((name, raw_value, value_type if value_type is not list else list))
    return variables


def prompt_value(name: str, raw_value: str, value_type: type) -> str:
    if value_type is list:
        default_text = raw_value
        prompt = f"Enter value for {name} as comma-separated list {default_text}: "
        value = input(prompt).strip()
        if not value:
            value = default_text
        if value.startswith("[") and value.endswith("]"):
            return value
        items = [item.strip() for item in value.split(",") if item.strip()]
        quoted = ", ".join(f'"{item}"' for item in items)
        return f"[{quoted}]"
    if value_type is int:
        prompt = f"Enter value for {name} [{raw_value}]: "
        value = input(prompt).strip()
        if not value:
            return raw_value
        return str(int(value))
    prompt = f'Enter value for {name} [{raw_value.strip("\"")}]: '
    value = input(prompt).strip()
    return f'"{value or raw_value.strip("\"")}"'


def write_tfvars(output_path: Path, values: dict[str, str]) -> None:
    lines = [f"{name} = {value}" for name, value in values.items()]
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Saved {output_path}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Generate a private Terraform tfvars file from the example template.")
    parser.add_argument("--terraform-dir", default="terraform", help="Terraform directory containing the example tfvars file")
    parser.add_argument("--force", action="store_true", help="Overwrite existing terraform.tfvars if present")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    base_dir = Path(__file__).resolve().parent
    terraform_dir = (base_dir / args.terraform_dir).resolve()
    example_path = terraform_dir / EXAMPLE_FILENAME
    output_path = terraform_dir / OUTPUT_FILENAME

    if not terraform_dir.is_dir():
        raise FileNotFoundError(f"Terraform directory not found: {terraform_dir}")
    if not example_path.exists():
        raise FileNotFoundError(f"Example file not found: {example_path}")
    if output_path.exists() and not args.force:
        print(f"File already exists: {output_path}")
        print("Use --force to overwrite the existing terraform.tfvars file.")
        return

    variables = parse_example(example_path)
    if not variables:
        raise ValueError(f"No variables found in example file: {example_path}")

    print("Generating terraform.tfvars from example. Press Enter to accept defaults.")
    values: dict[str, str] = {}
    for name, raw_value, value_type in variables:
        values[name] = prompt_value(name, raw_value, value_type)

    write_tfvars(output_path, values)


if __name__ == "__main__":
    main()
