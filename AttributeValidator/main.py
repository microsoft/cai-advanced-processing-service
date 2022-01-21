''' VALIDATION API '''
import json
import logging
import azure.functions as func

# Import custom modules
from . import helper

def main(req: func.HttpRequest, messageJSON) -> func.HttpResponse:
    message = json.loads(messageJSON)
    # Receive request and collect parameters
    try:
        req_body = req.get_json()
        module = req_body.get('module')
        values = req_body.get('values')
        region = req_body.get('region')
        manifest = req_body.get('manifest')
        # If no manifest has been passed, we take manifest.json by default
        if not manifest:
            manifest = 'manifest'
    except ValueError:
        pass
    finally:
        logging.info(f'[INFO] Set params -> module: {module} in {region}.')

    # Read manifest
    try:
        with open(f'{manifest}.json', 'r') as mf:
            manifest = json.load(mf)['AttributeValidator'][module]
    except FileNotFoundError:
        return func.HttpResponse("Manifest could not be found, please pass a valid manifest name.", status_code=400)
    except KeyError:
        return func.HttpResponse("API-specific manifest could not be loaded, please verify manifest and availability of requested module", status_code=400)

    # Create instance of class with module and (optional) region, as needed
    validation = helper.Validator(module, values, manifest, region)
    
    # Run validation if a respective matcher could be found
    if validation.matcher is not None:
        res = validation.run()
    else:
        return func.HttpResponse(f"This module is not known by the API, please select between {', '.join(manifest.keys())}", status_code=400)
    
    # Return set as json
    res = json.dumps(res, default=str)
    return func.HttpResponse(
            res, mimetype="application/json"
        )