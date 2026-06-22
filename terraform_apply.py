import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict


def run_terraform(directory: Path, terraform_bin: str, env: Dict[str, str]) -> None:
    commands = [
        [terraform_bin, 'init', '-input=false'],
        [terraform_bin, 'plan', '-out=tfplan', '-input=false'],
        [terraform_bin, 'apply', '-input=false', 'tfplan'],
    ]
    for command in commands:
        print('Running:', ' '.join(command))
        try:
            subprocess.run(command, cwd=directory, env=env, check=True)
        except FileNotFoundError as e:
            raise FileNotFoundError(
                f"Terraform executable not found: {terraform_bin!s}. "
                "Ensure Terraform is installed and available on PATH, or pass --terraform-bin with the full path. "
                "See https://learn.hashicorp.com/tutorials/terraform/install-cli for install instructions."
            ) from e
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Command failed: {' '.join(command)} (exit {e.returncode})") from e


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run Terraform for Home Assistant Docker deployment.')
    parser.add_argument('--terraform-dir', default='home-assistant/terraform', help='Terraform configuration directory')
    parser.add_argument('--docker-host', default='', help='Optional DOCKER_HOST override for Terraform provider')
    parser.add_argument('--terraform-bin', default='terraform', help='Terraform binary or full path to terraform executable')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    terraform_dir = Path(args.terraform_dir).resolve()
    if not terraform_dir.is_dir():
        raise FileNotFoundError(f'Terraform directory not found: {terraform_dir}')

    env = os.environ.copy()
    if args.docker_host:
        env['DOCKER_HOST'] = args.docker_host

    # Resolve terraform binary
    terraform_bin = args.terraform_bin
    found = shutil.which(terraform_bin)
    if not found:
        # If user provided a path, show helpful error; otherwise suggest install
        msg = (
            f"Terraform executable '{terraform_bin}' was not found on PATH. "
            "Install Terraform or provide the full path with --terraform-bin. "
            "See https://learn.hashicorp.com/tutorials/terraform/install-cli for guidance."
        )
        raise FileNotFoundError(msg)
    # Use the resolved full path to the binary
    terraform_bin = found

    run_terraform(terraform_dir, terraform_bin, env)


if __name__ == '__main__':
    main()
