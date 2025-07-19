from office365.sharepoint.client_context import ClientContext
from office365.runtime.auth.authentication_context import AuthenticationContext
from Sharepoint_Config import sharepoint
from io import BytesIO
import pandas as pd
from google.cloud import bigquery
import os
from Sharepoint_Config import get_db_config,database
import mysql.connector
from mysql.connector import Error
from sqlalchemy import create_engine
from google.oauth2 import service_account