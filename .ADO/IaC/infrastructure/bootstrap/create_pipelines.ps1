param (
    [Parameter(Mandatory = $True)][string]$project_name,
    [Parameter(Mandatory = $True)][string]$organization,
    [Parameter(Mandatory = $True)][string]$repository
 )

az pipelines create --name Terraform.DEV.CI --org $organization --project $project_name --repository $repository --branch develop --yaml-path /.pipelines/build/build_terraform_CI_DEV.yml --repository-type tfsgit --skip-first-run true
az pipelines create --name Terraform.PROD.CI --org $organization --project $project_name  --repository $repository --branch main --yaml-path /.pipelines/build/build_terraform_CI_PROD.yml --repository-type tfsgit --skip-first-run true 
az pipelines create --name Terraform.DEV.CD --org $organization --project $project_name  --repository $repository --branch develop --yaml-path /.pipelines/release/release_terraform_CD_DEV.yml --repository-type tfsgit --skip-first-run true 
az pipelines create --name Terraform.PROD.CD --org $organization --project $project_name  --repository $repository --branch main --yaml-path /.pipelines/release/release_terraform_CD_PROD.yml --repository-type tfsgit --skip-first-run true
