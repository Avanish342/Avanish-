
from Sharepoint_common_imports import *

def get_sharepoint_df(site_key, file_relative_path, sheet_name=None):
    """
    Load an Excel file from SharePoint and return a pandas DataFrame.
    
    :param site_key: Key from the config (e.g., 'analytics_etls')
    :param file_relative_path: File path relative to site's base path
    :param sheet_name: Optional sheet name in Excel file
    :return: pandas DataFrame
    """

    if site_key not in sharepoint:
        raise ValueError(f"SharePoint config not found for key: {site_key}")
    
    config = sharepoint[site_key]
    site_url = config['url']
    username = config['username']
    password = config['password']
    file_url = config['path'] + file_relative_path

    ctx_auth = AuthenticationContext(site_url)
    if not ctx_auth.acquire_token_for_user(username, password):
        raise ConnectionError("SharePoint authentication failed.")

    ctx = ClientContext(site_url, ctx_auth)
    file = ctx.web.get_file_by_server_relative_url(file_url)
    
    file_content = BytesIO()
    file.download(file_content)
    ctx.execute_query()
    
    file_content.seek(0)
    df = pd.read_excel(file_content, sheet_name=sheet_name)
    return df 


 # BQ Utility 
 # 
def upload_to_bigquery(df, table_name, config_key='big_query_credentials'):
    """ 
    Uploads a pandas DataFrame to BigQuery.
    
    :param df: pandas DataFrame
    :param table_name: Target BigQuery table name
    :param config_key: Key from config to load BQ credentials
    """
    config = get_db_config(config_key)

    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = config['credentials_path']

    client = bigquery.Client()
    table_id = f"{config['dataset_id']}.{table_name}"

    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE",  # Overwrites existing data
        autodetect=True                      # Automatically detects schema
    )

    try:
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Waits for job to complete
        print(f"✅ Successfully uploaded {job.output_rows} rows to {table_id}")
    except Exception as e:
        print(f"❌ Error uploading to BigQuery: {e}")
        raise  

def get_mysql_connection(config_key):
    config = database[config_key]
    try:
        conn = mysql.connector.connect(
            host=config['host_private'],  # or 'host_public'
            user=config['username'],
            password=config['password'],
            database=config['database_name']
        )
        if conn.is_connected():
            print("Connected to MySQL database")
            return conn
    except Error as e:
        print(f"Error: {e}")
        return None
conn = get_mysql_connection('central_data_mart')
if conn:
    cursor = conn.cursor()
    cursor.execute("SELECT DATABASE();")
    print("You're connected to database:", cursor.fetchone())
    cursor.close()
    conn.close()    

def run_mysql_query_to_df(config_key, query):
    config = database[config_key]
    try:
        conn = mysql.connector.connect(
            host=config['host_private'],  # or host_public
            user=config['username'],
            password=config['password'],
            database=config['database_name']
        )
        if conn.is_connected():
            print("Connected to MySQL database")
            df = pd.read_sql(query, conn)
            return df
    except Error as e:
        print(f"Error: {e}")
        return None
    finally:
        if conn.is_connected():
            conn.close()    


######################## CREATE and Load DF data To MYSQL Table ###########################################


def load_df_to_mysql_table(df, config_key, table_name, if_exists='replace'):
    """
    Uploads a pandas DataFrame to a MySQL table.
    
    :param df: DataFrame to upload
    :param config_key: Key in the database config dictionary
    :param table_name: Name of the table to create/overwrite
    :param if_exists: 'replace', 'append', or 'fail'
    """
    config = database[config_key]
    
    try:
        engine_url = f"mysql+mysqlconnector://{config['username']}:{config['password']}@{config['host_private']}/{config['database_name']}"
        engine = create_engine(engine_url)
        
        df.to_sql(name=table_name, con=engine, if_exists=if_exists, index=False)
        print(f"✅ Table `{table_name}` created and data loaded successfully.")
    except Exception as e:
        print(f"❌ Error loading data into MySQL: {e}")

########################################## BQ Query to DF ###################################################


def bq_query_to_df(query, credentials_path):
    """
    Executes a BigQuery SQL query and returns the result as a DataFrame.

    :param query: SQL query string
    :param credentials_path: Path to your service account JSON key
    :return: pandas.DataFrame
    """
    client = bigquery.Client.from_service_account_json(credentials_path)
    
    try:
        df = client.query(query).to_dataframe()
        print("✅ Query executed successfully.")
        return df
    except Exception as e:
        print(f"❌ Failed to execute query: {e}")
        return None
    
################################### INSERT DF TO BQ ##################################

def insert_df_to_bq(df, table_id, credentials_path):
    """
    Inserts a Pandas DataFrame into a BigQuery table.

    Args:
        df (pd.DataFrame): The DataFrame to upload.
        table_id (str): Full table ID in the format 'project.dataset.table'.
        credentials_path (str): Path to your service account JSON file.
    """
    try:
        # Load credentials and initialize client
        credentials = service_account.Credentials.from_service_account_file(credentials_path)
        client = bigquery.Client(credentials=credentials, project=credentials.project_id)

        # Configure job: append to table & autodetect schema
        job_config = bigquery.LoadJobConfig(
            write_disposition="WRITE_APPEND",  # or WRITE_TRUNCATE to replace
            autodetect=True,
        )

        # Load DataFrame to BigQuery
        job = client.load_table_from_dataframe(df, table_id, job_config=job_config)
        job.result()  # Wait for job to complete

        print(f"✅ Data inserted into BigQuery table: {table_id}")
    except Exception as e:
        print(f"❌ Error inserting into BigQuery: {e}")

       # Options for write_disposition:
#"WRITE_APPEND": Add to existing data 

#"WRITE_TRUNCATE": Overwrite entire table

#"WRITE_EMPTY": Only insert if table is empty

######################### INSERT DF TO MYSQL ####################################################################

def insert_df_to_mysql(df, table_name, config):
    """
    Insert a DataFrame into a MySQL table.

    Args:
        df (pd.DataFrame): Data to insert
        table_name (str): Name of the table
        config (dict): MySQL config with host, user, password, and database
    """
    try:
        # Create connection string
        conn_str = f"mysql+mysqlconnector://{config['username']}:{config['password']}@{config['host_private']}/{config['database_name']}"
        engine = create_engine(conn_str)

        # Upload the DataFrame
        df.to_sql(table_name, con=engine, if_exists='append', index=False)
        print(f"✅ Data inserted into MySQL table: {table_name}")
    except Exception as e:
        print(f"❌ Error inserting into MySQL: {e}")

#  "append" → Add to existing table ✅

#"replace" → Drop and recreate table

#"fail" → Raise error if table exists

      

