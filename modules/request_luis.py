'''MODULES USED ACROSS THE SOLUTION'''
import requests
import logging
import json
import os

# Define logger
logger = logging.getLogger(__name__)

# LUIS Scoring
def score_luis(text, luis_creds):
    """Score LUIS endpoint (REST API v3) and return parsed JSON"""

    # Set header/params for rest call
    params = {
        'q': text,
        'timezoneOffset': '0',
        'verbose': 'false',
        'spellCheck': 'false',
        'staging': 'false',
    }
    headers = {
        'Ocp-Apim-Subscription-Key': luis_creds['luis_key'],
    }

    # Set URL parameters to use in this REST call.
    params ={
        'query': text,
        'timezoneOffset': '0',
        'verbose': 'true',
        'show-all-intents': 'true',
        'spellCheck': 'false',
        'staging': 'false',
        'subscription-key': luis_creds['luis_key']
    }

    # Make the REST call.
    try:
        r = requests.get(f'https://{luis_creds["luis_prediction_endpoint"]}.cognitiveservices.azure.com/luis/prediction/v3.0/apps/{luis_creds["luis_id"]}/slots/{luis_creds["luis_slot"]}/predict', headers=headers, params=params)
        r = json.loads(r.text)
        logger.info('[INFO] - successfully processed LUIS request')
    except Exception as e:
        logger.error(f"[ERROR] LUIS encountered an issue -> {e}.")
    return r

def get_luis_creds(region=None):
    try:
        """Retrieve LUIS credentials from env variables or local config and return as dict"""
        luis_creds = dict()
        # If region is not None, we add a _ and the region parameter
        if region:
            _region = f'_{region}'
        else:
            _region = ""
        luis_creds['luis_id'] = os.environ.get(f'LUIS_ID{_region}')
        luis_creds['luis_key'] = os.environ.get(f'LUIS_KEY{_region}')
        luis_creds['luis_prediction_endpoint'] = os.environ.get(f'LUIS_PREDICTION_ENDPOINT{_region}')
        luis_creds['luis_slot'] = os.environ.get(f'LUIS_SLOT{_region}')
        # Local debugging
        if luis_creds['luis_key'] is None:
            logger.info(f'[INFO] Entering local debugging')
            import sys
            sys.path.append('./')
            import configparser
            config = configparser.ConfigParser()
            config.read('config.ini')
            luis_creds['luis_id'] = config[f'LUIS{_region}']['appid']
            luis_creds['luis_key'] = config[f'LUIS{_region}']['key']
            luis_creds['luis_prediction_endpoint'] = config[f'LUIS{_region}']['prediction_endpoint']
            luis_creds['luis_slot'] = config[f'LUIS{_region}']['slot']
    except KeyError:
        logger.error(f'[ERROR] - No valid luis credentials found. Please make sure you are using the correct region or whether there is region-neutral information set.')
        luis_creds = None
    return luis_creds