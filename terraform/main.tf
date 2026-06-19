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

# Woodpecker Management Server Container
resource "random_password" "woodpecker_secret" {
  length  = 32
  special = false
}

resource "docker_image" "woodpecker_server" {
  name = var.woodpecker_image
}

resource "docker_volume" "woodpecker_data" {
  name = var.woodpecker_data_volume
}

resource "docker_container" "woodpecker_server" {
  name  = "${var.stack_name}_woodpecker"
  image = docker_image.woodpecker_server.name
  restart = "always"

  ports {
    internal = 8000
    external = var.woodpecker_port
  }

  networks_advanced {
    name = docker_network.hass.name
  }

  mounts {
    target = "/data"
    source = docker_volume.woodpecker_data.name
    type   = "volume"
  }
  
  env = [
    "WOODPECKER_OPEN=true",
    "WOODPECKER_AGENT_SECRET=${random_password.woodpecker_secret.result}",
    "WOODPECKER_HOST=http://0.0.0.0:${var.woodpecker_port}"
  ]
}
