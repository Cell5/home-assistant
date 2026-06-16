import argparse
import os
import subprocess
from pathlib import Path
from typing import Dict


def run_terraform(directory: Path, env: Dict[str, str]) -> None:
    commands = [
        ['terraform', 'init', '-input=false'],
        ['terraform', 'plan', '-out=tfplan', '-input=false'],
        ['terraform', 'apply', '-input=false', 'tfplan'],
    ]
    for command in commands:
        print('Running:', ' '.join(command))
        subprocess.run(command, cwd=directory, env=env, check=True)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description='Run Terraform for Home Assistant Docker deployment.')
    parser.add_argument('--terraform-dir', default='home-assistant/terraform', help='Terraform configuration directory')
    parser.add_argument('--docker-host', default='', help='Optional DOCKER_HOST override for Terraform provider')
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    terraform_dir = Path(args.terraform_dir).resolve()
    if not terraform_dir.is_dir():
        raise FileNotFoundError(f'Terraform directory not found: {terraform_dir}')

    env = os.environ.copy()
    if args.docker_host:
        env['DOCKER_HOST'] = args.docker_host

    run_terraform(terraform_dir, env)


if __name__ == '__main__':
    main()
