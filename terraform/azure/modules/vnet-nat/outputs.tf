output "vnet_id" {
  value = azurerm_virtual_network.vnet.id
}

output "subnet_id" {
  value = azurerm_subnet.subnet.id
}

output "nat_gateway_id" {
  value = azurerm_nat_gateway.nat.id
}

output "public_ip" {
  value = azurerm_public_ip.nat_ip.ip_address
}