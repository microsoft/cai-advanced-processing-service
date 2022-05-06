import json
import logging
import time
import sys
import os
sys.path.append('./')
import LicensePlateRecognizer.main as lp
import azure.functions as func
import pandas as pd

# set environmental variables
with open('./local.settings.json', 'r') as f:
  setting = json.load(f)

evns = setting['Values']
for key, value in evns.items():
    os.environ[key] = value # visible in this process + all children
    
df = pd.read_csv('./tests/files/lpr_rec_orig.csv')

test_org =  df.lexical_rec.values 
test_query = df.lexical_rec.apply(lambda x: 'das ist '+x).values

test_lp = df.lp.values

start =  time.time()
errors = []
print("query, lpr_result, lpr, cplquery, luis_entity, issue ")
for query, lps, org in zip(test_query, test_lp, test_org):
    try:
        body = {'query':query,
                 "language": "de-de",
                 "locale": "de"
                 }
        
        # Build HTTP request
        req = func.HttpRequest(
            method  = 'GET',
            body    = json.dumps(body).encode('utf8'),
            url     = '/api/LicensePlateRecognizer',
            params  = {}
        )
        # Call the function.
        res = json.loads(lp.main(req).get_body())
        try: 
            res_entity = res['cplEntities'][0]['entity']
        except:
            res_entity = ''
        if res_entity != lps:
            # print(print('\033[91m' + query + '\033[0m'))
            # print(print('\033[100m' + lps + '\033[0m'))
            if res['entities'][0]['text'] != org:
                print(org + ", " + res_entity + ", "  + lps + ", " + res['cplQuery'] + ", " + res['entities'][0]['text'] + ", luis")
            else:
                print(org + ", " + res_entity + ", "  + lps + ", " + res['cplQuery'] + ", " + res['entities'][0]['text'] + ", voice" )
            logging.warning(f'[ERROR] LP Recognition mismatch for {query} -> {lps} != {res}')
            errors.append(query)
    except Exception as e:
        logging.warning(query, e, res)
        print(org + ", " + res_entity + ", "  + lps + ", , , voice" )
        errors.append(query)

end = time.time() - start

print(f'[INFO] DONE -> {1 - (len(errors)/len(test_query)):.2%}. \n\tTotal duration \t\t{end:.3}s \n\tDuration per loop \t{end/len(test_query):.3} \n\tno. of the error: {len(errors)} \n\tno of tests: {len(test_query)}s')