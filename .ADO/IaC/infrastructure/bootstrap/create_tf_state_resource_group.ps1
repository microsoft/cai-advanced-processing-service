param (
    [Parameter(Mandatory = $True)] [string] $resource_group_name,
    [Parameter(Mandatory = $True)] [string] $storage_account_name,
    [string] $storage_container_name = "tfremotestoragecontainer",
    [string]$state_file_name = "terraform.tfstate",
    [string]$location = "westeurope"
 )

#az login

az group create --location $location --name $resource_group_name

az storage account create --name $storage_account_name --resource-group $resource_group_name --sku Standard_LRS --kind StorageV2 --encryption-services blob --access-tier Cool --allow-blob-public-access false
az storage container create --name $storage_container_name --account-name $storage_account_name

$subscription_id = $(az account show --query id -o tsv)
$tenant_id = $(az account show --query tenantId -o tsv)

terraform init -backend-config=storage_account_name="$storage_account_name" -backend-config=container_name="$storage_container_name" -backend-config=key="$state_file_name" -backend-config=resource_group_name="$resource_group_name" -backend-config=subscription_id="$($subscription_id)" -backend-config=tenant_id="$($tenant_id)"
