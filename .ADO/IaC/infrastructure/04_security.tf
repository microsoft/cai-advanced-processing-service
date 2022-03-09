module "vnet" {
  source = "./modules/vnet"
  naming_convention = local.naming_convention
  resource_group = azurerm_resource_group.solution_accelarator.name
  depends_on = [
    azurerm_resource_group.solution_accelarator
  ]
}


