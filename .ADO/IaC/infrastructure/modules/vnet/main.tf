data "azurerm_resource_group" "rg" {
  name = var.resource_group
}

resource "azurerm_virtual_network" "vnet" {
  name                     = "vnet${var.naming_convention}"
  resource_group_name      = data.azurerm_resource_group.rg.name
  location                 = data.azurerm_resource_group.rg.location
  address_space            = ["10.0.0.0/16"]
}

resource "azurerm_subnet" "storage" {
  name                 = "storage_subnet${var.naming_convention}"
  resource_group_name  = data.azurerm_resource_group.rg.name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes           =  ["10.0.1.0/24"]
  enforce_private_link_endpoint_network_policies = true
}  

