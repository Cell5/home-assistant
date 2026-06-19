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

resource "docker_image" "jenkins" {
  name = var.jenkins_image
}

resource "docker_volume" "jenkins_home" {
  name = "${var.stack_name}_jenkins_home"
}

resource "docker_container" "jenkins" {
  name  = "${var.stack_name}_jenkins"
  image = docker_image.jenkins.name
  user  = "root" # needed for docker.sock access
  restart = "always"

  ports {
    internal = 8080
    external = var.jenkins_http_port
  }

  ports {
    internal = 50000
    external = var.jenkins_agent_port
  }

  networks_advanced {
    name = docker_network.hass.name
  }

  mounts {
    target = "/var/jenkins_home"
    source = docker_volume.jenkins_home.name
    type   = "volume"
  }

  mounts {
    target = "/var/run/docker.sock"
    source = "/var/run/docker.sock"
    type   = "bind"
  }
}
