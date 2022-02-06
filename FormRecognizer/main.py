''' FORM RECOGNIZER FUNCTION '''
import json
import logging
import azure.functions as func
from azure.ai.formrecognizer import FormRecognizerClient
from azure.core.credentials import AzureKeyCredential
from datetime import datetime
import uuid

# Import custom modules
from modules.retrieve_credentials import CredentialRetriever
from modules.data_connector import DataConnector
from assets.constants import (
    CONFIG,
    FORM_RECOGNIZER,
    MANIFEST,
    FORM_REGOGNIZER_ENV
)

def main(req: func.HttpRequest) -> func.HttpResponse:
    logging.info('Python HTTP trigger function processed a request.')

    # Get request body
    try:
        req_body = req.get_json()
        model_id    = req_body.get('model_id')
        doc_url     = req_body.get('doc_url')
        copy_to_blob = True if req_body.get('copy_to_blob') else False
        logging.warning('No parameter for copy_to_blob received, taking False as default')
        manifest    = req_body.get(MANIFEST)
        # If no manifest has been passed, we take manifest.json by default
        if not manifest:
            logging.info(f'[INFO] - No manifest name passed in the request, fallback to "{MANIFEST}.json."')
            manifest = MANIFEST
    except ValueError:
        pass

    # Read manifest and extract module information
        try:
            with open(f'{manifest}.json', 'r') as mf:
                _manifest       =  json.load(mf)
                manifest        = _manifest[FORM_RECOGNIZER]
        except FileNotFoundError:
            return func.HttpResponse("Manifest could not be found, please pass a valid manifest name.", status_code=400)

    # Retrieve credentials and set up data connector
    credentials = CredentialRetriever(FORM_REGOGNIZER_ENV).load_credentials()
    connector = DataConnector(FORM_REGOGNIZER_ENV, manifest.get(CONFIG), credentials).connector
    
    # Process request
    if all([model_id, doc_url]):
        logging.info('Received both required parameters model_id and doc_url')
        # Initiate client and send request
        try:
            form_recognizer_client = FormRecognizerClient(
                f"https://{credentials.get('FORM_RECOGNIZER_NAME')}.cognitiveservices.azure.com", 
                AzureKeyCredential(credentials.get('FORM_RECOGNIZER_KEY'))
            )
            poller = form_recognizer_client.begin_recognize_custom_forms_from_url(model_id = model_id, form_url = doc_url)
            result = poller.result()
        except Exception as e:
            logging.error(f'[ERROR] - {e}')
            return func.HttpResponse(
                "[ERROR] - Request to Form Recognizer failed. Check logs for endpoint/credentialm, model ID or file type issues.",
                status_code = 400
            )

        # Filter results for desired keys
        filtered_results = {key: result[0].fields[key] for key in return_keys.split(",")}

        # Pack return json
        return_dict = {}
        for name, field in filtered_results.items():
            logging.info(f'{name} -> {field.value}')
            return_dict[name] = field.value

        # Catch if missing values
        if None in return_dict.values():
            logging.warning('Found missing values in response object, may be wrong form or a missing field.')
            return func.HttpResponse(
                "Wrong form or missing values, please validate the posted form.",
                status_code = 202
            )

        # Write to BLOB storage
        if copy_to_blob:
            try:
                meta_dict = {'PartitionKey': 'FormData', 'RowKey': uuid.uuid4().hex, 'time': datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")}
                data_connector.push_data_to_table(connection_data, {**meta_dict, **return_dict})
                logging.info('Pushed data to table storage')
                storage = {
                    'copy_to_blob': copy_to_blob, 
                    'success': True
                }
            except Exception as e:
                logging.error(f'Copy to blob failed -> {e}')
                storage = {
                    'copy_to_blob': copy_to_blob, 
                    'success': False
                }
        else:
            storage = {
                'copy_to_blob': copy_to_blob
            }

        # Return json
        res = json.dumps(dict(
            results = return_dict,
            storage = storage))
        return func.HttpResponse(
            res, mimetype = "application/json"
            )

    # If model_id does not exist
    elif not model_id:
        logging.error('Request failed, please pass a valid model_id.')
        return func.HttpResponse(
             "Pass model id",
             status_code = 400
        )

    # If doc_url does not exist
    elif not doc_url:
        logging.error('Request failed, please pass a valid document url.')
        return func.HttpResponse(
             "Pass URL",
             status_code = 400
        )