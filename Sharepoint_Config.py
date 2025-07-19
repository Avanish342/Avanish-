
# Sharepoint Path

sharepoint = {
    'Collection_Tracker': {
        'url': 'https://moglix.sharepoint.com/sites/AnalyticsETL',
        'path': '/sites/AnalyticsETL/ETLs/',
        'username': 'centralsyncreports@moglix.com',
        'password': 'shgmsfvhhzhjywkw'
    }}

# BQ Path
database = {
    'big_query_credentials': {
        'credentials_path': r'C:\Users\avanish.kumar\Downloads\reports\Sharepoint_BQ_ETL\BQ.json',
        'dataset_id': 'moglix-analytics-datalake.Analytics_AR',
        'dataset_name': 'Analytics_Als'
    }
}

def get_db_config(config_key):
    return database[config_key]
######################################MYSQL HOST ###########################################################

database['central_data_pool'] = { #13.234.107.34   10.0.4.124
    'host_private': '10.0.4.124',
    'host_public':'13.234.107.34',
    'username': 'etl',
    'password': 'dE#2aQ!12aw',
    'database_name': 'central_data_pool',
    'receiver_mail': ['avanish.kumar@moglix.com']
}

database["central_data_sink"] = {
    "host_private": '10.0.2.11',
    "host_public": "35.154.255.26", #public 35.154.255.26 10.0.2.11
    "username": "freq_report",
    "password": "freq#mog@321",
    "database_name": "central_data_sink",
}

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

database['analytics_reporting'] = { #35.154.255.26   10.0.2.117
    'host_private': '10.0.2.117',
    'host_public':'35.154.255.26',
    'username': 'etl',
    'password': 'Etl@1@#$%',
    'database_name': 'analytics_reporting',
    'receiver_mail': ['avanish.kumar@moglix.com']
}