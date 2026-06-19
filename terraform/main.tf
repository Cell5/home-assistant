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
