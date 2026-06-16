terraform {
  required_version = ">= 1.3.0"

  required_providers {
    docker = {
      source  = "kreuzwerker/docker"
      version = "~> 2.0"
    }
  }
}

provider "docker" {
  host = var.docker_host
}

resource "docker_network" "hass" {
  name = "${var.stack_name}_network"
}

resource "docker_volume" "homeassistant_config" {
  name = "${var.stack_name}_homeassistant_config"
}

resource "docker_volume" "zigbee2mqtt_data" {
  name = "${var.stack_name}_zigbee2mqtt_data"
}

resource "docker_volume" "mosquitto_data" {
  name = "${var.stack_name}_mosquitto_data"
}

resource "docker_image" "homeassistant" {
  name = var.homeassistant_image
}

resource "docker_image" "zigbee2mqtt" {
  name = var.zigbee2mqtt_image
}

resource "docker_image" "mosquitto" {
  name = var.mosquitto_image
}

resource "docker_container" "mqtt" {
  name  = "${var.stack_name}_mqtt"
  image = docker_image.mosquitto.latest
  restart = "always"

  ports {
    internal = 1883
    external = var.mqtt_port
  }

  ports {
    internal = 9001
    external = var.mqtt_websocket_port
  }

  networks_advanced {
    name = docker_network.hass.name
  }

  mounts {
    target = "/mosquitto/data"
    source = docker_volume.mosquitto_data.name
    type   = "volume"
  }
}

resource "docker_container" "zigbee2mqtt" {
  name  = "${var.stack_name}_zigbee2mqtt"
  image = docker_image.zigbee2mqtt.latest
  restart = "always"

  ports {
    internal = 8080
    external = var.zigbee_port
  }

  env = [
    "TZ=${var.timezone}",
    "MQTT_SERVER=tcp://${var.mqtt_broker_name}:1883",
  ]

  networks_advanced {
    name = docker_network.hass.name
  }

  mounts {
    target = "/app/data"
    source = docker_volume.zigbee2mqtt_data.name
    type   = "volume"
  }

  devices = var.zigbee_devices
  depends_on = [docker_container.mqtt]
}

resource "docker_container" "homeassistant" {
  name  = "${var.stack_name}_homeassistant"
  image = docker_image.homeassistant.latest
  restart = "always"

  ports {
    internal = 8123
    external = var.homeassistant_port
  }

  env = [
    "TZ=${var.timezone}",
  ]

  networks_advanced {
    name = docker_network.hass.name
  }

  mounts {
    target = "/config"
    source = docker_volume.homeassistant_config.name
    type   = "volume"
  }

  depends_on = [docker_container.zigbee2mqtt]
}
