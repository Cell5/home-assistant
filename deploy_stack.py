import argparse
import subprocess
import sys
from pathlib import Path
import textwrap

COMPOSE_TEMPLATE = textwrap.dedent('''
services:
  homeassistant:
    image: ghcr.io/home-assistant/home-assistant:stable
    container_name: {stack_name}_homeassistant
    restart: always
    ports:
      - "8123:8123"
    volumes:
      - {config_dir}:/config
    depends_on:
      - mqtt

  mqtt:
    image: eclipse-mosquitto:latest
    container_name: {stack_name}_mqtt
    restart: always
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - {mqtt_data}:/mosquitto/data
      - {mqtt_log}:/mosquitto/log

  zigbee2mqtt:
    image: koenkk/zigbee2mqtt:latest
    container_name: {stack_name}_zigbee2mqtt
    restart: always
    depends_on:
      - mqtt
    ports:
      - "8080:8080"
    environment:
      - TZ=UTC
      - MQTT_SERVER=tcp://mqtt:1883
    volumes:
      - {zigbee_data}:/app/data
{devices_section}
''')


def build_compose_content(stack_name: str, config_dir: Path, mqtt_data: Path, mqtt_log: Path, zigbee_data: Path, zigbee_device: str) -> str:
    devices_section = ''
    if zigbee_device:
        devices_section = textwrap.dedent(f'''
    devices:
      - "{zigbee_device}:{zigbee_device}"
''')
    return COMPOSE_TEMPLATE.format(
        stack_name=stack_name,
        config_dir=config_dir.as_posix(),
        mqtt_data=mqtt_data.as_posix(),
        mqtt_log=mqtt_log.as_posix(),
        zigbee_data=zigbee_data.as_posix(),
        devices_section=devices_section,
    )


def run_docker_compose(compose_file: Path) -> None:
    command = ['docker', 'compose', '-f', str(compose_file), 'up', '-d']
    print('Running:', ' '.join(command))
    subprocess.run(command, check=True)


def parse_args():
    parser = argparse.ArgumentParser(description='Generate and deploy Home Assistant Docker stack with Zigbee2MQTT support.')
    parser.add_argument('--stack-name', default='home-assistant', help='Docker stack and container name prefix')
    parser.add_argument('--zigbee-device', default='', help='Host Zigbee adapter device path (e.g. /dev/ttyACM0)')
    parser.add_argument('--compose-output', default='docker-compose.yaml', help='Output Compose file path')
    parser.add_argument('--config-dir', default='home-assistant/config', help='Host config directory for Home Assistant')
    parser.add_argument('--mqtt-data', default='home-assistant/mosquitto/data', help='Host directory for MQTT broker data')
    parser.add_argument('--mqtt-log', default='home-assistant/mosquitto/log', help='Host directory for MQTT broker logs')
    parser.add_argument('--zigbee-data', default='home-assistant/zigbee2mqtt/data', help='Host directory for Zigbee2MQTT data')
    parser.add_argument('--up', action='store_true', help='Run docker compose up after generating the file')
    return parser.parse_args()


def main():
    args = parse_args()
    compose_path = Path(args.compose_output).resolve()
    config_dir = Path(args.config_dir).resolve()
    mqtt_data = Path(args.mqtt_data).resolve()
    mqtt_log = Path(args.mqtt_log).resolve()
    zigbee_data = Path(args.zigbee_data).resolve()

    config_dir.mkdir(parents=True, exist_ok=True)
    mqtt_data.mkdir(parents=True, exist_ok=True)
    mqtt_log.mkdir(parents=True, exist_ok=True)
    zigbee_data.mkdir(parents=True, exist_ok=True)

    compose_content = build_compose_content(
        stack_name=args.stack_name,
        config_dir=config_dir,
        mqtt_data=mqtt_data,
        mqtt_log=mqtt_log,
        zigbee_data=zigbee_data,
        zigbee_device=args.zigbee_device,
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
