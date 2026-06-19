output "network_name" {
  description = "Docker network created for Home Assistant"
  value       = docker_network.hass.name
}
