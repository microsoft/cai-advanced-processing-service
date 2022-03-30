import json
import logging
import time
import sys
import os
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



test_query = [
    'Hello World',
    'Philipp.dangelmaier@daimlerdot.com.',
    'dijankad@hotmail.de',
    'Michael Punkt Mueller at G mail.de.',
    'can.tuerkel@adesso.de.',
    'can.tuerkel@adesso.de',
    'can.tuerkel@adesso.de',
    'Michael.meyer@gmail.com.',
    'can.tuerkel@adesso.de',
    'ABC at T Punkt F.',
    'Philipp Punkt Dangelmaier hat Daimler dot.com.',
    'Mina.mueller@gmail.com.',
    'Mittelseestr 8.',
    'Philipp dangelmaier@daimlerdot.com.',
    'Nina.mueller@gmail.com.',
    'Philipp Punkt, Dangelmaier, Hartmut Set, Mercedes benzdot.com.',
    'Gabrielasabatini@web.de.',
    'Christoph kunze@xy.de.',
    'Patrick Punkt GERSCHEL at.',
    'Janka edadesso.de.',
    'Nina.mueller@adesso.de.',
    'Zara.schmidt@adesso.de.',
    'Philipp Punkt, Dangelmaier, Daimler, dot.com.',
    'Miriam.buettnerat-web.de.',
    'Normen.meyer@daimler.com.',
    'Sebastian.navrath@daimler.com.',
    'Petra.bartel@daimler.com.',
    'Magdalena minus Winkler at GM x.de.',
    'Janine.illing@yahoo.de.',
    'Alfred.hitchcock@hotmaildot.com.',
    'Heinrich.schwabauer@daimler.com.',
    'Helena.schmidt@daimlerdot.com.',
    'Helena.schmidt@daimlerdot.com.',
    'Helena.schmidt@daimler.com',
    'Sabine scholl@hotmaildot.com.',
    'Marcel@web.de.',
    'max.mustermann@gmail.com',
    'max@test.de',
    'Normen.meyerdaimler.com.',
    'Zara.vogel@daimler.com.',
    'N Punkt wiedich@daimler.com.',
    'Klaus Punkt unterberger at T minus online.de.',
    'Haben Sie? 080382. Unterstrich 82. At yahoo.de.',
    'Stefan Schwabe at GM x.de.',
    'Max.mustermann@web.de.',
    'Eins23@yahoo.de.',
    'Helena. Punkt schmidt@daimlerdot.com.',
    'Taxi quaxi add on.at.',
    'Das war Klaus Minus Bindel Meyer. At thieme.com.',
    'Hakan Punkt Kick. At aol.com.',
    'Laura Punkt Gouda. At. Web.de.',
    'Meine Emailadresse ist Max Punkt mustermann. At gmail.com.',
    'Meyer Punkt, J 6 und zwanzig@gmail.com.',
    'E Mail ADOU. GAS. At. Die male.com. Also die em ail.com.',
    'ALE. XAN. D. Okay. R. Punkt. RIT. T. SCH. Ja. Zelt. GM. X. Punkt net.',
    'Das ist Nordpol Berta Punkt. Konrad Richard, Anton, Viktor, Martha, Anton, at Gustav Anton. Punkt Info.',
    'MA. GDALENA. Punkt w IH NKLER. Ed DAIMLER. Punkt COM.',
    'Klarer.weberat-web.de.',
    'Eins23@yahoo.com.',
    'ULRIKE Punkt QUAST AT. DAIMLER Punkt. COM.',
    'Um HELENA Punkt SCHMIDT at DAIMLER Punkt. COM.',
    'Sonja Punkt bÃ¼cken at Gmail, dot.com.',
    'Ihr braucht keine Emailadresse von mir soll denn das?',
    'Siegfried, Emil, Berta, Anton, Siegfried, Theodor, Ida, Anton. Punkt Nordpol Anton Walter, Richard Anton, Theodor Heinrich at. Dora Anton, Ida, Martha, Ludwig emilrichard.com'
    ]

test_email = [
    '',
    'philipp.dangelmaier@daimler.com',
    'dijankad@hotmail.de',
    'michael.mueller@gmail.de',
    'can.tuerkel@adesso.de',
    'can.tuerkel@adesso.de',
    'can.tuerkel@adesso.de',
    'michael.meyer@gmail.com',
    'can.tuerkel@adesso.de',
    '',
    '',
    'mina.mueller@gmail.com',
    '',
    'dangelmaier@daimler.com',
    'nina.mueller@gmail.com',
    '',
    'gabrielasabatini@web.de',
    'kunze@xy.de',
    '',
    '',
    'nina.mueller@adesso.de',
    'zara.schmidt@adesso.de',
    '',
    '',
    'normen.meyer@daimler.com',
    'sebastian.navrath@daimler.com',
    'petra.bartel@daimler.com',
    'magdalena-winkler@gmx.de',
    'janine.illing@yahoo.de',
    'alfred.hitchcock@hotmail.com',
    'heinrich.schwabauer@daimler.com',
    'helena.schmidt@daimler.com',
    'helena.schmidt@daimler.com',
    'helena.schmidt@daimler.com',
    'scholl@hotmail.com',
    'marcel@web.de',
    'max.mustermann@gmail.com',
    'max@test.de',
    '',
    'zara.vogel@daimler.com',
    'wiedich@daimler.com',
    'klaus.unterberger@t-online.de',
    '080382._82.@yahoo.de',
    'sschwabe@gmx.de',
    'max.mustermann@web.de',
    'eins23@yahoo.de',
    'schmidt@daimler.com',
    '',
    'meyer.@thieme.com',
    'hakan.kick.@aol.com',
    'laura.gouda.@web.de',
    'max.mustermann.@gmail.com',
    'zwanzig@gmail.com',
    '',
    '',
    'b.kravma@ganton.info',
    '',
    '',
    'eins23@yahoo.com',
    'ulrike.quast@daimler.com',
    'helena.schmidt@daimler.com',
    'sonja.bã¼cken@gmail.com',
    '',
    'sebastianton.nawalterrath@daimlemilrichard.com'
]

email_recognized_list =[
    
    ]

start =  time.time()
errors = []
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
      print(query +", '" + email + "'" )
      
    except Exception as e:
        # print(print('\033[91m' + query + '\033[0m'))
        print(query + ", ''")
        logging.warning(query, e)
        
    if email != test:
      errors.append(query)
        
print(len(test_query))
end = time.time() - start
print(errors)
print(f'[INFO] DONE -> {1 - (len(errors)/len(test_email)):.2%}. \n\tno. of the error: {len(errors)} \n\tno of tests: {len(test_email)}')
