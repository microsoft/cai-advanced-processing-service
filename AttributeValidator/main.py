''' VALIDATION API '''
import json
import logging
import azure.functions as func

# Import custom modules and helpers
from . import helper

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Receive request and collect parameters
    try:
        req_body = req.get_json()
        module = req_body.get('module')
        region = req_body.get('region')
        manifest = req_body.get('manifest')
        values = req_body.get('values')
        logging.warning(values)
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
            _manifest_file = json.load(mf)['AttributeValidator']['modules']
            manifest = _manifest_file[module]
    except FileNotFoundError:
        return func.HttpResponse("Manifest could not be found, please pass a valid manifest name.", status_code=400)
    except KeyError:
        return func.HttpResponse(f"This module is not known by the manifest, please select between {', '.join(_manifest_file.keys())}.", status_code=400)

    # Create instance of class with module and (optional) region, as needed
    validation = helper.Validator(module, values, manifest, region)
    
    # Run validation if a respective matcher could be found
    if validation.matcher and validation.ready_to_run:
        res = validation.matcher.run()
    elif not validation.matcher:
        return func.HttpResponse(f"This module is known by the manifest, yet not in the processing logic. Please validate code version or select between {', '.join(_manifest_file.keys())}.", status_code=400)
    elif validation.matcher and not validation.ready_to_run:
        return func.HttpResponse(f"The values you passed do not match to the module you requested.", status_code=400)

    # Return set as json
    #res = json.dumps(res, default=str)
    return func.HttpResponse(
            res, 
            mimetype="application/json"
        )