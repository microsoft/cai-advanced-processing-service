''' TABLE REQUESTOR API '''
import logging
import json
import azure.functions as func

# Import custom modules
from modules.retrieve_credentials import CredentialRetriever
from modules.data_connector import DataConnector
from assets.constants import (
    CONFIG,
    MANIFEST,
    TABLE_REQUESTOR,
    TABLE_REQUESTOR_ENV
)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    # Receive request
    try:
        req_body    = req.get_json()
        table_name  = req_body.get('table').get('name')
        params      = req_body.get('params')
        manifest    = req_body.get(MANIFEST)
        # If no manifest has been passed, we take manifest.json by default
        if not manifest:
            logging.info(f'[INFO] - No manifest name passed in the request, fallback to "{MANIFEST}.json."')
            manifest = MANIFEST
    except Exception as e:
        logging.error(f"[ERROR] - Failed to parse arguments -> {e}")
        table_name = False
        params = False

    # Read manifest and extract module information
    try:
        with open(f'{manifest}.json', 'r') as mf:
            _manifest       =  json.load(mf)
            manifest        = _manifest[TABLE_REQUESTOR]
    except FileNotFoundError:
        return func.HttpResponse("Manifest could not be found, please pass a valid manifest name.", status_code=400)

    # Retrieve credentials and set up data connector
    credentials = CredentialRetriever(TABLE_REQUESTOR_ENV).load_credentials()
    connector = DataConnector(TABLE_REQUESTOR_ENV, manifest.get(CONFIG), credentials).connector

    # Process request
    if all([table_name, params]):
        # Request data from storage
        try:
            customer_data = connector.get_data(table_name, params)
        except Exception as e:
            logging.error(f'Failed to establish connection to table storage -> {e}')
            return func.HttpResponse(
                "[ERROR] - Connection to table storage could not be established, please verify the connection string and table name.",
                status_code = 400
             )
        # Return set as json
        res = json.dumps(dict(results = customer_data), default=str)
        return func.HttpResponse(res, mimetype="application/json")
    else:
        return func.HttpResponse(
             "[ERROR] - Pass a table and set of variables you want to look up in the customer data base, for example:\n {'table': {'name': 'UserData'}, 'params': {'PartitionKey': 'UserData'}}.",
             status_code = 400
        )
