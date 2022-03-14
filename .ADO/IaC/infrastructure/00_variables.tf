######################################################
# VARIABLES
######################################################

variable "TEAM_NAME" {
  type        = string
  description = "Name of the Team resources are provisioned for"
}

variable "STAGE_NAME" {
  type        = string
  description = "Name of the Stage resources are provisioned for"
}

variable "LOCATION" {
  default     = "West Europe"
  description = "Location of the cloud resources"
}

variable "STAGE_NUMBER" {
  type        = string 
  description = "Number to distingish versioning between same stages"
}





