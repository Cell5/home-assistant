# Home Assistant Deployment

This folder contains deployment infrastructure for a Home Assistant Docker stack with Zigbee2MQTT support.

## Contents

- `Jenkinsfile` - pipeline to run Terraform and deploy the Docker stack.
- `deploy_stack.py` - Python script to generate a Docker Compose manifest and start the stack.
- `terraform_apply.py` - Python wrapper to initialize and apply Terraform configuration.
- `terraform/` - Terraform configuration to provision Docker network, volumes, and containers.
- `.gitignore` - ignores generated artifacts and local runtime files.

## Requirements

- Docker with `docker compose` support
- Terraform 1.3+ with Docker provider ([Install Terraform](https://developer.hashicorp.com/terraform/tutorials/aws-get-started/install-cli))
- Python 3.10+
- Jenkins agent with Docker and Terraform installed for CI

## Quick start

1. Generate a private Terraform variable file from the example and keep it out of source control:

    ```bash
    python home-assistant/generate_tfvars.py --terraform-dir terraform
    ```

    If `terraform/terraform.tfvars` already exists, run with `--force` to overwrite.

2. Provision infrastructure with Terraform:

    ```bash
    python home-assistant/terraform_apply.py --terraform-dir home-assistant/terraform
    # or specify terraform binary location if it is not in the PATH
    python terraform_apply.py --terraform-dir home-assistant/terraform --terraform-bin /path/to/terraform/bin
    ```

    This creates the Docker network, volumes, and pulls any required images. It does not start the application containers.

    Optionally, Terraform can also provision a Jenkins container to run pipelines. If you set `jenkins_image` and ports in `terraform/terraform.tfvars`, Terraform will create a `jenkins` container attached to the same network.

3. Generate and deploy the stack with Docker Compose:

    ```bash
    python deploy_stack.py --stack-name home-assistant --zigbee-device /dev/ttyUSB0 --up
    ```

4. Access Home Assistant at `http://localhost:8123`.

## Notes

- `deploy_stack.py` creates a `docker-compose.yaml` file in the `home-assistant` folder.
- `terraform/` creates Docker volumes and network resources for the stack.
- The current setup uses an MQTT broker container (`eclipse-mosquitto`) for Zigbee2MQTT.
