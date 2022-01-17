''' AUTHENTICATION API '''
import re
import json
import logging
import azure.functions as func

# Import custom modules
try:
    from __app__.assets import characters
    from __app__.modules import request_table as request
    from __app__.modules import resolve_spelling as resolve
    from __app__.modules import pattern_matcher as patterns
    from __app__.modules import similarity_score as simscore
    import __app__.helper as helper
except Exception as e:
    logging.info('[INFO] Helper: Using local imports.')
    from assets import characters
    from modules import request_table as request
    from modules import resolve_spelling as resolve
    from modules import pattern_matcher as patterns
    from modules import similarity_score as simscore
    from . import helper

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Load connection string
    auth_attributes = helper.get_connection_data(['USER_STORAGE_CONNECTION_STRING', 'AUTHENTICATION_TABLE'])

    # Assemble connectiond ata
    connection_data = {'table_name': auth_attributes['AUTHENTICATION_TABLE'], 'connection_string': auth_attributes['USER_STORAGE_CONNECTION_STRING'].replace('"', "")}
    
    # Receive request and collect parameters
    try:
        req_body = req.get_json()
        attributes = req_body.get('attributes')
        method = req_body.get('method')
        lang = req_body.get('locale')
        manifest = req_body.get('manifest')
        if not method:
            method = 4
        # If no locale has been passed, we take EN by default
        if not lang:
            lang = 'en'
        # If no manifest has been passed, we take manifest.json by default
        if not manifest:
            manifest = 'manifest'
        # Set verbose flag if wanted, but disable it in general for any stage that goes beyond DEV
        verbose = req_body.get('verbose')
        # verbose = False # If verbose parameter wants to be declined in general
    except ValueError:
        pass
    finally:
        logging.info(f'[INFO] Set params -> method: {str(method)}, language: {lang}, manifest: {manifest}.json.')

    # Create instance of class
    cleaner = resolve.CleanText(lang)

    # Read manifest
    try:
        with open(f'{manifest}.json', 'r') as mf:
            manifest = json.load(mf)
    except FileNotFoundError:
        return func.HttpResponse("Manifest could not be loaded, you have to pass a valid manifest name.", status_code=400)

    # Quit, if too few attributes have been passed
    if len(attributes) < manifest.get('config')['min_attributes']:
        return func.HttpResponse("You have to pass at least two additional attributes for authentication.", status_code=400)

    # Check if request attributes in manifest
    if not set(attributes.keys()) <= set(manifest.get('attributes').keys()):
        return func.HttpResponse("One or multiple arguments passed via request are not part of the manifest.", status_code=400)

    # Check if required attributes are there
    if not set([key for key, value in manifest.get('attributes').items() if manifest.get('attributes')[key]['required']]) <= set(attributes.keys()):
        return func.HttpResponse("Not all required arguments have been passed.")

    # Preprocess user id first, as we need it for the lookup
    cleaned = {}
    cleaned['Id'] = cleaner.clean_repeats(cleaner.resolve_numbers_as_words(attributes['Id'])).replace(' ', '')
    # Pop 'Id', as we will loop through the other ones in the next step
    attributes.pop('Id')

    # Gather data from database
    try:
        customer_data = request.get_data_from_table(connection_data = connection_data, table_filters = {'PartitionKey': connection_data['table_name'], 'RowKey': cleaned['Id']})
        logging.info(f'Received response with data from backend, loaded {len(customer_data)} data set(s).')
    except Exception as e:
        logging.error(f'Could not load user dict -> {e}.')
        return func.HttpResponse('Backend request failed, please check logs for further information.')

    # Clean attributes to bring them into a unified format, unless too few attributes passed
    if len(customer_data) > 0:
        # Filter customer data set for attributes needed
        customer_data = {key:value for key, value in customer_data[0].items() if key in attributes.keys()}
        for key, value in attributes.items():
            # Check if preprocessing is needed
            if manifest.get('attributes')[key]['preprocess']:
                cleaned[key] = cleaner.clean_attribute(value)
            else:
                cleaned[key] = value
    else:
        return func.HttpResponse('No user record found.')
        
    # Define checks
    checks = {
        1: simscore.apply_check_1,
        2: simscore.apply_check_2,
        3: simscore.apply_check_3
    }

    # If method is between 1 and 3, it will exclusively be applied
    if method in range(1, 4):
        match = checks[method](customer_data, cleaned, manifest.get('attributes'))
    # If not (which means it is > 3) we apply all checks
    else:
        for check in range(1, 4):
            match = checks[check](customer_data, cleaned, manifest.get('attributes'))
            if all(match.values()):
                logging.info(f'Reached match stage at {str(check)}, breaking loop.')
                break
    
    # Return verbose information
    if verbose:
        logging.warning(f'Customer data: {customer_data}.')
        logging.warning(f'Cleaned request: {cleaned}.')
        response_json = dict(result = dict(authenticated = all(match.values())), verbose = dict(attributes = match, method = method))
    else:
        response_json = dict(result = dict(authenticated = all(match.values())))
    
    # Return set as json
    res = json.dumps(response_json, default=str)
    return func.HttpResponse(
            res, mimetype="application/json"
        )