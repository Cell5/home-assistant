variable "docker_host" {
  description = "Docker host address for the Terraform provider"
  type        = string
  default     = "unix:///var/run/docker.sock"
}

variable "stack_name" {
  description = "Prefix used for Docker resources"
  type        = string
  default     = "home-assistant"
}

variable "timezone" {
  description = "Timezone used by containers"
  type        = string
  default     = "UTC"
}

variable "homeassistant_image" {
  description = "Home Assistant Docker image"
  type        = string
  default     = "ghcr.io/home-assistant/home-assistant:stable"
}

variable "zigbee2mqtt_image" {
  description = "Zigbee2MQTT Docker image"
  type        = string
  default     = "koenkk/zigbee2mqtt:latest"
}

variable "mosquitto_image" {
  description = "MQTT broker Docker image"
  type        = string
  default     = "eclipse-mosquitto:latest"
}

variable "mqtt_broker_name" {
  description = "Docker network hostname for the MQTT broker"
  type        = string
  default     = "mqtt"
}

variable "zigbee_devices" {
  description = "List of host Zigbee device paths exposed to the Zigbee2MQTT container"
  type        = list(string)
  default     = []
}
