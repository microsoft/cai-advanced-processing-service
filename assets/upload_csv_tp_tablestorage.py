import pandas as pd  
from azure.cosmosdb.table import TableService  

connection_string = '<connection-string>'
csvfile = "./AttributeValidatorStreets_TableExport.csv"
table_name = csvfile.replace(".csv","")
table_name = table_name.replace("./","")
table_name = table_name.replace("_TableExport","")
table_name = table_name.replace("_Sample","")
# table_name='JAGOTESTSTREETS'

def setTable(table_name,table,table_service):  
   index=0 
   # Save table header in list
   list_header = table.columns
   # Save each row as list
   list_of_lists = table.values.tolist()
   for row in list_of_lists:
        task = {}
        for ele in row:
            task[list_header[row.index(ele)]]=str(ele)
        print(task)
        table_service.insert_or_replace_entity(table_name, task, timeout=None)
        index=index+1
   return True  

# Read data from csv file
df_csv = pd.read_csv(csvfile, sep=",", encoding="utf-8")
# Connect to Table Storage
table_service = TableService(connection_string=connection_string)
# Create table
res_table = table_service.create_table(table_name) #creating table
if res_table == False:
    print("Table already exists or could not be created.",res_table)
else:
    print("Table created.",res_table)
# Upload data to table
res = setTable(table_name, df_csv, table_service) #inserting csv to cloud   
if res == True:
    print("Upload successful.")
else:
    print("Upload failed.")
