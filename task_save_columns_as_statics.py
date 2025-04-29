import boto3
import pandas as pd
import psycopg2
from io import BytesIO
from sqlalchemy import create_engine, text
import logging
logging.basicConfig(level=logging.INFO, filename='.venv/logs/update_table_columns.log', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')

# AWS + S3 setup
s3 = boto3.client('s3')
bucket_name = 'primelab-calculated-metrics'
prefix = ''

# DB connection
engine = create_engine("postgresql://dev:dev@localhost:5432/prime_web_test")

def list_parquet_files(bucket, prefix):
    paginator = s3.get_paginator('list_objects_v2')
    pages = paginator.paginate(Bucket=bucket, Prefix=prefix)
    for page in pages:
        for obj in page.get('Contents', []):
            if obj['Key'].endswith('.parquet'):
                yield obj['Key']

def extract_columns_from_s3(s3_key):
    obj = s3.get_object(Bucket=bucket_name, Key=s3_key)
    df = pd.read_parquet(BytesIO(obj['Body'].read()), engine='pyarrow')
    return df.columns.tolist()

def store_metadata_to_db(table_name, column_names):
    rows = [(table_name, col) for col in column_names]
    df_meta = pd.DataFrame(rows, columns=["table_name", "column_name"])
    df_meta['data_source'] = df_meta['table_name'].str.split('/').str[0]
    df_meta['table_name'] = df_meta['table_name'].str.split('/').str[1]
    df_meta.to_sql("table_columns", engine, schema='backend', if_exists="append", index=False, method="multi")

def is_table_already_stored(data_source, table_name):
    query = f"""
    SELECT 1 FROM backend.table_columns
    WHERE data_source = '{data_source}' AND table_name = '{table_name}'
    LIMIT 1;
    """
    with engine.connect() as conn:
        return conn.execute(text(query)).fetchone() is not None
    

def main():
    stored_tables = []
    for key in list_parquet_files(bucket_name, prefix):
        data_source, table_name, _ = key.split('/')
        if (data_source, table_name) in stored_tables or is_table_already_stored(data_source, table_name):
            print(f"❌ {key} already exists.")
            logging.warning(f"❌ {key} already exists.")
            continue
        try:
            column_names = extract_columns_from_s3(key)
            store_metadata_to_db(key, column_names)
            stored_tables.append((data_source, table_name))
            print(f"✅ {key} inserted.")
            logging.info(f"✅ {key} inserted.")
        except Exception as e:
            print(f"❌ Error with {key}: {e}")
            logging.error(f"❌ Error with {key}: {e}")

if __name__ == "__main__":
    main()