# Introduction 
This forlder is to depoly the CAI architeture in AZure using Terraform and ADO CD/CI pipeline.

# Prerequisite
1. [Azure CLI](https://docs.microsoft.com/de-de/cli/azure/install-azure-cli)
2. [Azure DevOps CLI](https://docs.microsoft.com/de-de/azure/devops/cli/?view=azure-devops)
3. [Terraform](https://learn.hashicorp.com/tutorials/terraform/install-cli)
4. [Service Connection for Pipelines](https://docs.microsoft.com/de-de/azure/devops/pipelines/library/service-endpoints?view=azure-devops&tabs=yaml)

# Setup for Local Development

1. az login
2. az account set --subscription <name or id>
3. Import (Create an empty repo in some Project and use this Git as import Url) and Clone this repository
4. Create a backend for local development
   1. ``cd infrastructure``
   2. ``bootstrap/create_tf_state_resource_group.ps1 -resource_group_name <ResourceGroupName> -storage_account_name <StorageAccountName>``
5. The Command account will create .terraform folder with a connection to the backend

# Setup CI/CD

1. Push the Repo to your Azure Dev Ops
2. Create a Develop branch
3. Setup your Service Connections and use them as parameter in all Yaml Files in "/.pipelines/release/stages/*.yml"
4. Create the pipelines with executing the following script
   1. ``cd infrastructure``
   2. ``bootstrap/create_pipelines.ps1 -project_name <NameOfTtheProject> -repository <RepositoryName> -organization <OrganizationUrl>``

Now you are done, the develop pipeline will trigger automatically and apply changes automaticlly to your infrastructure.
The pipeline for the masterbranch has to be triggered manually