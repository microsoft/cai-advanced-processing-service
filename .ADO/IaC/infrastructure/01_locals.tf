##################################################################################
# Locals
##################################################################################

locals {
  # replace empty strings with dashes, to be used as git repo names
  team_name = lower(replace(var.TEAM_NAME, " ", "-"))
  stage = lower(var.STAGE_NAME)
  stage_number = lower(var.STAGE_NUMBER)
  location = lower(var.LOCATION)
  naming_convention      = "${local.team_name}${local.stage}${local.stage_number}"
  # tagging 
  default_tags = {
    ApplicationName = "${local.team_name}${local.stage}${local.stage_number}"
    Env             = local.stage
    Owner           = local.team_name
  }
}
