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
- Terraform 1.3+ with Docker provider
- Python 3.10+
- Jenkins agent with Docker and Terraform installed for CI

## Quick start

1. Provision infrastructure with Terraform:

    ```bash
    python home-assistant/terraform_apply.py --terraform-dir home-assistant/terraform
    ```

2. Generate and deploy the stack:

    ```bash
    python home-assistant/deploy_stack.py --stack-name home-assistant --zigbee-device /dev/ttyUSB0 --up
    ```

3. Access Home Assistant at `http://localhost:8123`.

## Notes

- `deploy_stack.py` creates a `docker-compose.yaml` file in the `home-assistant` folder.
- `terraform/` creates Docker volumes and network resources for the stack.
- The current setup uses an MQTT broker container (`eclipse-mosquitto`) for Zigbee2MQTT.
