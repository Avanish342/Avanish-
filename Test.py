from google.cloud import bigquery
import pandas as pd
import io
from office365.runtime.auth.user_credential import UserCredential
from office365.sharepoint.client_context import ClientContext

# Set your credentials file
bq_client = bigquery.Client.from_service_account_json("path/to/BQ.json")

# Step 1: Fetch metadata table from BQ
metadata_query = """
SELECT Functional_Area, Folder, URL, Path, File, Sheet_Name, User_Name, Password, DB_Type,
       Project_Id, Schema, Table, Created_At, Schedule_Time, Frequency
FROM `your_project.your_dataset.your_metadata_table`
"""
metadata_df = bq_client.query(metadata_query).to_dataframe()

# Step 2: Loop through each row
for _, row in metadata_df.iterrows():
    if row["DB_Type"] != "BQ":
        continue

    # Construct SharePoint file path
    sharepoint_url = row["URL"]
    full_file_path = row["Path"] + row["File"]

    # Authenticate to SharePoint
    ctx = ClientContext(sharepoint_url).with_credentials(
        UserCredential(row["User_Name"], row["Password"])
    )
    response = ctx.web.get_file_by_server_relative_url(full_file_path).download()
    ctx.execute_query()

    # Read Excel from bytes
    excel_bytes = io.BytesIO(response.content)
    df = pd.read_excel(excel_bytes, sheet_name=row["Sheet_Name"])

    # Step 3: Push to BQ table
    table_id = f"{row['Project_Id']}.{row['Schema']}.{row['Table']}"
    job = bq_client.load_table_from_dataframe(df, table_id, job_config=bigquery.LoadJobConfig(
        write_disposition="WRITE_TRUNCATE"  # Overwrites table each time
    ))
    job.result()
    print(f"✅ Loaded data to: {table_id}")

print("🎉 All tables created/updated successfully.")