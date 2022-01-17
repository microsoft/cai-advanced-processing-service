''' VALIDATION API '''
import json
import logging
import azure.functions as func

# Import custom modules
try:
    import __app__.helper as helper
except Exception as e:
    logging.info('[INFO] Helper: Using local imports.')
    from . import helper

def main(req: func.HttpRequest) -> func.HttpResponse:
    # Receive request and collect parameters
    try:
        req_body = req.get_json()
        module = req_body.get('module')
        values = req_body.get('values')
        region = req_body.get('region')
    except ValueError:
        pass
    finally:
        logging.info(f'[INFO] Set params -> module: {module} in {region}.')

    # Create instance of class with module and (optional) region, as needed
    validation = helper.Validator(module, region)
    # Run validation
    res = validation.run()
    
    # Return set as json
    res = json.dumps(res, default=str)
    return func.HttpResponse(
            res, mimetype="application/json"
        )