output "network_name" {
  description = "Docker network created for Home Assistant"
  value       = docker_network.hass.name
}

output "jenkins_container" {
  description = "Name of the Jenkins container"
  value       = docker_container.jenkins.name
}
