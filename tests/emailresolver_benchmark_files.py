import json
import logging
import time
import sys
import os
import pandas as pd
# sys.path.insert(1, '..')
sys.path.append("./")
import AttributeValidator.main as av
import azure.functions as func

# set environmental variables
with open('./local.settings.json', 'r') as f:
  setting = json.load(f)

evns = setting['Values']
for key, value in evns.items():
    os.environ[key] = value # visible in this process + all children

df = pd.read_csv('./tests/files/synth_mails_rec_orig.csv')


test_query = df.lexical_rec.values
test_email = df.mail.apply(lambda x: x.lower()).values

email_recognized_list =[
    
    ]

start =  time.time()
errors = []
print("query, email_result, email, issue")
for query, test in zip(test_query, test_email):

    try:
      body = {
            "module": "email",
            "locale": "de",
            "region": "de",
            "values": {"query": query}
            }
        
      # Build HTTP request
      req = func.HttpRequest(
          method  = 'GET',
          body    = json.dumps(body).encode('utf8'),
          url     = '/api/AttributeValidator',
          params  = {}
      )
      # Call the function.
      res = json.loads(av.main(req).get_body())
      email = res["e-mail"]
    #   print(print('\033[106m' + query + '\033[0m'))
      # print(query +", '" + email + "'" )
      
    except Exception as e:
        # print(print('\033[91m' + query + '\033[0m'))
        print(query + ", ''")
        logging.warning(query, e)
        
    if (email != '') & (email != test):
      errors.append(query)
      # print(print('\033[91m' + query + ": " + email + " != "  + test + '\033[0m'))
      print(query + ", " + email + ", "  + test + ", voice" )
      
      
        
print(len(test_query))
end = time.time() - start
print(errors)
print(f'[INFO] DONE -> {1 - (len(errors)/len(test_email)):.2%}. \n\tno. of the error: {len(errors)} \n\tno of tests: {len(test_email)}')
