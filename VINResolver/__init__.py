import logging
import json

import azure.functions as func

# Define global logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
formatter = logging.Formatter(fmt='%(asctime)s %(name)s %(message)s',
                                  datefmt='%m/%d/%Y %I:%M:%S %p')
for handler in logger.handlers:
    if isinstance(handler, logging.Streamhandler):
        handler.setFormatter(formatter)

# Import custom modules
try:
    from  __app__.modules.libvin import Vin
    logger.info("[INFO] Helper: Using app imports.")
except Exception as e:
    logger.info("[INFO] Helper: Using local imports.")
    from  modules.libvin import Vin


def main(req: func.HttpRequest) -> func.HttpResponse:
    logger.info('[INFO] VINResolver Post Processing started.')

    # Get query and request parameters
    try:
        req_body = req.get_json()
        query = req_body.get('query')
        expectedwmi = req_body.get('expectedwmi')
        lang = req_body.get('locale')
    except Exception as e:
        logger.info(f'[INFO] Trying to receive request via params -> {e}')
        query = req.params.get('query')
        expectedwmi = req.params.get('expectedwmi')
        lang = req.params.get('locale')
    finally:    
        # Fill eventually missing params with default ones
        if not lang:
            lang = 'de'
        if  not expectedwmi:
            expectedwmi = 'WDC'
        
        # Snip off everything after first three characters 
        expectedwmi = expectedwmi[:3]
         # Snip off everything after first two characters (e.g. en-us -> en)
        lang = lang[:2]
        logger.info(f'[INFO] Set params -> expectedwmi: {expectedwmi}, language: {lang}.')

    
    # If query is not empty, go ahead
    if query:
        # Get VIN entity results
        v = Vin(query)
        
        # if VIN is valid, go ahead
        if v.is_valid:
            ## Pack json response
            res = json.dumps(
                {
                    "query": query,
                    "validvin": True,
                    "expectedwmi": expectedwmi,
                    "vindetails": {
                        "region": v.region,
                        "country": v.country,
                        "year": v.year,
                        "make": v.make,
                        "manufacturer": v.manufacturer,
                        "is_pre_2010": v.is_pre_2010,
                        "wmi": v.wmi,
                        "vds": v.vds,
                        "vis": v.vis,
                        "vsn": v.vsn,
                        "less_than_500_built_per_year": v.less_than_500_built_per_year
                    }
                })
            
            
        else:
            ## Pack json response
            res = json.dumps(
                {
                "query": query,
                "validvin": False,
                "vindetails": {}
                })

        return func.HttpResponse(
            res, mimetype='application/json'
        )    
    else:
        return func.HttpResponse(
             "[ERROR] Received a blank request. Please pass a value using the defined format. Example: \{'query':'AB C 1234'\}",
             status_code = 400
        )

