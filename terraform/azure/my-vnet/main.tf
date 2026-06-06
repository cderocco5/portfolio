provider "azurerm" {
  features {}
}

resource "azurerm_resource_group" "rg" {
  name     = "rg-demo-network"
  location = "East US"
}

module "vnet_nat" {
  source = "../modules/vnet-nat"

  resource_group_name = azurerm_resource_group.rg.name
  location            = azurerm_resource_group.rg.location

  vnet_name     = "demo-vnet"
  address_space = ["10.0.0.0/16"]

  subnet_name   = "app-subnet"
  subnet_prefix = "10.0.1.0/24"

  nat_gateway_name = "demo-nat"
  public_ip_name   = "demo-nat-ip"
}