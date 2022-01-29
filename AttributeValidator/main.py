''' VALIDATION API '''
import json
import logging
import azure.functions as func

# Import custom modules and helpers
from . import helper
from assets.constants import ATTRIBUTE_VALIDATOR, CONFIG, MANIFEST, MODULE, MODULES, REGION, VALUES

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Receive request and collect parameters
    try:
        req_body    = req.get_json()
        module      = req_body.get(MODULE)
        region      = req_body.get(REGION)
        manifest    = req_body.get(MANIFEST)
        values      = req_body.get(VALUES)
        # If no manifest has been passed, we take manifest.json by default
        if not manifest:
            logging.info(f'[INFO] - No manifest name passed in the request, fallback to "{MANIFEST}.json"')
            manifest = 'manifest'
        if not module:
            return func.HttpResponse("[ERROR] - Received bad request body: missing module declaration.", status_code=400)
        logging.info(f'[INFO] Set params -> module: {module} in {region}.')
    except ValueError:
        return func.HttpResponse("[ERROR] - Received bad request body: format of request body not valid.", status_code=400)
    
    # Read manifest and extract module information
    try:
        with open(f'{MANIFEST}.json', 'r') as mf:
            _manifest       =  json.load(mf)
            manifest        = _manifest[ATTRIBUTE_VALIDATOR]
        # Load module to check whether it is available in the manifest - otherwise we enforce a KeyError
        manifest[MODULES][module]
    except FileNotFoundError:
        return func.HttpResponse("Manifest could not be found, please pass a valid manifest name.", status_code=400)
    except KeyError:
        return func.HttpResponse(f"This module is not known by the manifest, please select between: {', '.join(manifest[MODULES].keys())}.", status_code=400)

    # Create instance of class with module and (optional) region, as needed
    validation = helper.Validator(module, manifest, values, region)
    
    # Run validation if a respective matcher could be found
    if validation.matcher and validation.ready_to_run:
        res = validation.matcher.run()
        return func.HttpResponse(res, mimetype="application/json")
    elif not validation.matcher:
        return func.HttpResponse(f"This module is known by the manifest, yet not in the processing logic. Please validate code version or select between {', '.join(manifest[MODULES].keys())}.", status_code=400)
    elif validation.matcher and not validation.ready_to_run:
        return func.HttpResponse(f"The values you passed do not match to the module you requested: {validation.message}.", status_code=400)