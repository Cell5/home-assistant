output "network_name" {
  description = "Docker network created for Home Assistant"
  value       = docker_network.hass.name
}

output "homeassistant_container" {
  description = "Name of the Home Assistant container"
  value       = docker_container.homeassistant.name
}

output "zigbee2mqtt_container" {
  description = "Name of the Zigbee2MQTT container"
  value       = docker_container.zigbee2mqtt.name
}

output "mqtt_container" {
  description = "Name of the MQTT broker container"
  value       = docker_container.mqtt.name
}
