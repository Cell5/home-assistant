import argparse
import subprocess
import sys
import re
from pathlib import Path
import textwrap
from typing import Any

COMPOSE_TEMPLATE = textwrap.dedent('''
services:
  homeassistant:
    image: {homeassistant_image}
    container_name: {stack_name}_homeassistant
    restart: always
    depends_on:
      - mqtt
    ports:
      - "{homeassistant_port}:8123"
    volumes:
      - {config_dir}:/config
    networks:
      - {network_name}

  mqtt:
    image: {mosquitto_image}
    container_name: {stack_name}_mqtt
    restart: always
    ports:
      - "{mqtt_port}:1883"
      - "{mqtt_websocket_port}:9001"
    volumes:
      - {mqtt_config}:/mosquitto/config
      - {mqtt_data}:/mosquitto/data
      - {mqtt_log}:/mosquitto/log
    networks:
      - {network_name}

  zigbee2mqtt:
    image: {zigbee2mqtt_image}
    user: "1000:1000"
    group_add:
        - dialout
    container_name: {stack_name}_zigbee2mqtt
    restart: always
    depends_on:
      - mqtt
    ports:
      - "{zigbee_port}:8080"
    environment:
      - TZ={timezone}
      - MQTT_SERVER=tcp://{mqtt_broker_name}:1883
    volumes:
      - {zigbee_data}:/app/data
      - /run/udev:/run/udev:ro
    networks:
      - {network_name}
{devices_section}

networks:
  {network_name}:
    external: true
''')

TFVARS_DEFAULT = 'terraform/terraform.tfvars'
TFVARS_PATTERN = re.compile(r'^\s*([a-zA-Z0-9_]+)\s*=\s*(.+)$')
DEFAULT_MOSQUITTO_CONF = textwrap.dedent('''
    persistence true
    persistence_location /mosquitto/data/
    log_dest file /mosquitto/log/mosquitto.log
    listener 1883
    allow_anonymous true
''')


def parse_tfvars(path: Path) -> dict[str, Any]:
    values: dict[str, Any] = {}
    text = path.read_text(encoding='utf-8')
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith('#'):
            continue
        match = TFVARS_PATTERN.match(stripped)
        if not match:
            continue
        key, raw_value = match.groups()
        raw_value = raw_value.split('#', 1)[0].strip()
        if raw_value.startswith(('"', "'")) and raw_value.endswith(('"', "'")):
            values[key] = raw_value[1:-1]
        elif raw_value.startswith('[') and raw_value.endswith(']'):
            items = [item.strip() for item in raw_value[1:-1].split(',') if item.strip()]
            normalized = [item[1:-1] if item.startswith(('"', "'")) and item.endswith(('"', "'")) else item for item in items]
            values[key] = normalized
        else:
            try:
                values[key] = int(raw_value)
            except ValueError:
                values[key] = raw_value
    return values


def build_compose_content(
    stack_name: str,
    config_dir: Path,
    mqtt_config: Path,
    mqtt_data: Path,
    mqtt_log: Path,
    zigbee_data: Path,
    zigbee_devices: list[str],
    image_names: dict[str, str],
    mqtt_broker_name: str,
    timezone: str,
    ports: dict[str, int],
) -> str:
    devices_section = ''
    if zigbee_devices:
        device_lines = '\n'.join(f'      - "{device}:/dev/ttyUSB0"' for device in zigbee_devices)
        devices_section = f'    devices:\n{device_lines}\n'
    return COMPOSE_TEMPLATE.format(
        homeassistant_image=image_names['homeassistant_image'],
        mosquitto_image=image_names['mosquitto_image'],
        zigbee2mqtt_image=image_names['zigbee2mqtt_image'],
        stack_name=stack_name,
        config_dir=config_dir.as_posix(),
        mqtt_config=mqtt_config.as_posix(),
        mqtt_data=mqtt_data.as_posix(),
        mqtt_log=mqtt_log.as_posix(),
        zigbee_data=zigbee_data.as_posix(),
        mqtt_port=ports['mqtt_port'],
        mqtt_websocket_port=ports['mqtt_websocket_port'],
        zigbee_port=ports['zigbee_port'],
        homeassistant_port=ports['homeassistant_port'],
        mqtt_broker_name=mqtt_broker_name,
        timezone=timezone,
        devices_section=devices_section,
        network_name=f'{stack_name}_network',
    )


def run_docker_compose(compose_file: Path) -> None:
    command = ['docker', 'compose', '-f', str(compose_file), 'up', '-d']
    print('Running:', ' '.join(command))
    subprocess.run(command, check=True)


def resolve_path(path: str, base_dir: Path) -> Path:
    candidate = Path(path)
    return candidate.resolve() if candidate.is_absolute() else (base_dir / candidate).resolve()


def parse_args():
    parser = argparse.ArgumentParser(description='Generate and deploy Home Assistant Docker stack with Zigbee2MQTT support.')
    parser.add_argument('--stack-name', default='hass', help='Docker stack and container name prefix')
    parser.add_argument('--zigbee-device', default='', help='Host Zigbee adapter device path (e.g. /dev/ttyACM0)')
    parser.add_argument('--tfvars', default=TFVARS_DEFAULT, help='Path to terraform.tfvars with deployment variables')
    parser.add_argument('--compose-output', default='docker-compose.yaml', help='Output Compose file path')
    parser.add_argument('--config-dir', default=None, help='Host config directory for Home Assistant')
    parser.add_argument('--mqtt-config', default=None, help='Host directory for MQTT broker configuration')
    parser.add_argument('--mqtt-data', default=None, help='Host directory for MQTT broker data')
    parser.add_argument('--mqtt-log', default=None, help='Host directory for MQTT broker logs')
    parser.add_argument('--zigbee-data', default=None, help='Host directory for Zigbee2MQTT data')
    parser.add_argument('--up', action='store_true', help='Run docker compose up after generating the file')
    return parser.parse_args()


def main():
    args = parse_args()
    base_dir = Path(__file__).resolve().parent
    tfvars_path = resolve_path(args.tfvars, base_dir)
    compose_path = resolve_path(args.compose_output, base_dir)

    if tfvars_path.exists():
        tfvars_values = parse_tfvars(tfvars_path)
    else:
        print(f'Warning: tfvars file not found at {tfvars_path}, using defaults.')
        tfvars_values = {}

    image_names = {
        'homeassistant_image': tfvars_values.get('homeassistant_image', 'ghcr.io/home-assistant/home-assistant:stable'),
        'mosquitto_image': tfvars_values.get('mosquitto_image', 'eclipse-mosquitto:latest'),
        'zigbee2mqtt_image': tfvars_values.get('zigbee2mqtt_image', 'koenkk/zigbee2mqtt:latest'),
    }

    ports = {
        'homeassistant_port': tfvars_values.get('homeassistant_port', 8123),
        'mqtt_port': tfvars_values.get('mqtt_port', 1883),
        'mqtt_websocket_port': tfvars_values.get('mqtt_websocket_port', 9001),
        'zigbee_port': tfvars_values.get('zigbee_port', 8686),
    }

    stack_name = tfvars_values.get('stack_name', args.stack_name)
    timezone = tfvars_values.get('timezone', 'UTC')
    mqtt_broker_name = tfvars_values.get('mqtt_broker_name', 'mqtt')

    if args.zigbee_device:
        zigbee_devices = [args.zigbee_device]
    else:
        zigbee_devices = tfvars_values.get('zigbee_devices', [])

    config_dir = resolve_path(
        args.config_dir if args.config_dir else f'{stack_name}/config',
        base_dir,
    )
    mqtt_config = resolve_path(
        args.mqtt_config if args.mqtt_config else f'{stack_name}/mosquitto/config',
        base_dir,
    )
    mqtt_data = resolve_path(
        args.mqtt_data if args.mqtt_data else f'{stack_name}/mosquitto/data',
        base_dir,
    )
    mqtt_log = resolve_path(
        args.mqtt_log if args.mqtt_log else f'{stack_name}/mosquitto/log',
        base_dir,
    )
    zigbee_data = resolve_path(
        args.zigbee_data if args.zigbee_data else f'{stack_name}/zigbee2mqtt/data',
        base_dir,
    )

    config_dir.mkdir(parents=True, exist_ok=True)
    mqtt_config.mkdir(parents=True, exist_ok=True)
    mqtt_data.mkdir(parents=True, exist_ok=True)
    mqtt_log.mkdir(parents=True, exist_ok=True)
    zigbee_data.mkdir(parents=True, exist_ok=True)

    mosquitto_conf_path = mqtt_config / 'mosquitto.conf'
    if not mosquitto_conf_path.exists():
        mosquitto_conf_path.write_text(DEFAULT_MOSQUITTO_CONF, encoding='utf-8')
        print(f'Created default Mosquitto config at {mosquitto_conf_path}')

    compose_content = build_compose_content(
        stack_name=stack_name,
        config_dir=config_dir,
        mqtt_config=mqtt_config,
        mqtt_data=mqtt_data,
        mqtt_log=mqtt_log,
        zigbee_data=zigbee_data,
        zigbee_devices=zigbee_devices,
        image_names=image_names,
        mqtt_broker_name=mqtt_broker_name,
        timezone=timezone,
        ports=ports,
    )

    compose_path.write_text(compose_content, encoding='utf-8')
    print(f'Generated Docker Compose file at {compose_path}')

    if args.up:
        try:
            run_docker_compose(compose_path)
        except subprocess.CalledProcessError as exc:
            print('Failed to start Docker stack:', exc, file=sys.stderr)
            sys.exit(exc.returncode)


if __name__ == '__main__':
    main()
