##################################################################################
# Resource group
##################################################################################

resource "azurerm_resource_group" "solution_accelarator" {
  name     = "cai_${local.naming_convention}_rg"
  location = local.location
  #Show without lifecycle
  lifecycle {
    ignore_changes = [
      name,
      location,
    ]
  }
}
