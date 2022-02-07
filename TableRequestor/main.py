''' TABLE REQUESTOR API '''
import logging
import json
import azure.functions as func

# Import custom modules
from modules import data_connector

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Python HTTP trigger function processed a request.")

    # Receive request
    try:
        req_body = req.get_json()
        table_name = req_body['table']['name']
        params = req_body['params']
    except Exception as e:
        logging.error(f"[ERROR] - Failed to parse arguments -> {e}")
        table_name = False
        params = False

    # Load connection string
    auth_attributes = data_connector.get_table_creds(['USER_STORAGE_CONNECTION_STRING'])

    # Process request
    if all([table_name, params]):
        connection_data = {'table_name': table_name, 'connection_string': auth_attributes['USER_STORAGE_CONNECTION_STRING'].replace('"', "")}
        # Request data from storage
        try:
            customer_data = data_connector.get_data_from_table(connection_data, params)
        except Exception as e:
            logging.error(f'Failed to establish connection to table storage -> {e}')
            return func.HttpResponse(
                "[ERROR] - Connection to table storage could not be established, please verify the connection string and table name.",
                status_code=400
             )
        # Return set as json
        res = json.dumps(dict(results = customer_data), default=str)
        return func.HttpResponse(res, mimetype="application/json")
    else:
        return func.HttpResponse(
             "[ERROR] - Pass a table and set of variables you want to look up in the customer data base, for example:\n {'table': {'name': 'UserData'}, 'params': {'PartitionKey': 'UserData'}}.",
             status_code=400
        )
