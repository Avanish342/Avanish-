from Sharepoint_Utility import get_sharepoint_df
from Sharepoint_Utility import upload_to_bigquery
import pandas as pd
from Sharepoint_Utility import run_mysql_query_to_df
from Sharepoint_Utility import load_df_to_mysql_table
from Sharepoint_Utility import load_df_to_mysql_table,bq_query_to_df


########################## Sharepoint data to DF #################################################
df = get_sharepoint_df(
    site_key='Collection_Tracker',
    file_relative_path='Collection Tracker/Collection_Tracker.xlsx',
    sheet_name='NET_OD_OS'
)

print(df.head())
numeric_columns = ['Net_OD', 'Net_OS_0_30']

for col in numeric_columns:
    df[col] = df[col].replace(r'^\s*-+\s*$', '0', regex=True)  # Replace dashes
    df[col] = pd.to_numeric(df[col], errors='coerce')      

y = df

########################### UPLOAD DF DATA TO BQ TABLE ###############################################
#upload_to_bigquery(y, table_name='test_table')
#print(y.head())
######################################### MYSQL QUERY TO DF  ##################################################
query = "SELECT * FROM Fact_Sales LIMIT 10;"
df1 = run_mysql_query_to_df('central_data_mart', query)

if df is not None:
    print(df1.head())
#
######################## CREATE and Load DF data To MYSQL Table ###########################################


# load_df_to_mysql_table(df, config_key='central_data_mart', table_name='test_sales_table')

############################### BQ query to DF #################################################################

query = """
SELECT * FROM `moglix-analytics-datalake.Analytics_AR.AR_Collection_Tracker_Collection` LIMIT 10
"""

df = bq_query_to_df(query, r'C:\Users\avanish.kumar\Downloads\reports\Sharepoint_BQ_ETL\BQ.json')

print(df.head())


############################## Insert df to BQ table ############################################################

# BigQuery table and credentials path
table_id = 'your-project-id.your_dataset.your_table'
credentials_path = r'C:\Users\avanish.kumar\Downloads\reports\Sharepoint_BQ_ETL\BQ.json'

# Insert to BQ
insert_df_to_bq(df, table_id, credentials_path)

################################ Insert df to MYSQL TABLE ############################

# MySQL config (example from your earlier message)
database = {
    'central_data_mart': {
        'host_private': '10.0.4.124',
        'host_public': '13.234.107.34',
        'username': 'etl',
        'password': 'dE#2aQ!12aw',
        'database_name': 'central_data_mart',
        'receiver_mail': ['avanish.kumar@moglix.com']
    }
}

# Insert DataFrame
insert_df_to_mysql(df, 'your_table_name', database['central_data_mart'])

