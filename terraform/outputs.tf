output "network_name" {
  description = "Docker network created for Home Assistant"
  value       = docker_network.hass.name
}

output "woodpecker_container" {
  description = "Name of the Woodpecker server container"
  value       = docker_container.woodpecker_server.name
}

output "woodpecker_agent_secret" {
  value     = random_password.woodpecker_secret.result
  sensitive = true
}
