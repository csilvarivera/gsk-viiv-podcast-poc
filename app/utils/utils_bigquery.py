import bigframes.pandas as bf
import pandas as pd

def initialze_bigquery(location, project_id):
    bf.reset_session()
    bf.options.bigquery.location = location #this variable is set based on the dataset you chose to query
    bf.options.bigquery.project = project_id #this variable is set based on the dataset you chose to query and where your BigQuery environment

def get_podcasts( project_id:str, bq_dataset:str, bq_table:str):
  """ Obtain podcast previously saved in BQ """
  df = bf.read_gbq("{0}.{1}.{2}".format(project_id, bq_dataset, bq_table))
  return df.to_pandas()

def save_to_podcast(df,project_id,bq_dataset, bq_table):
  insert_df = bf.read_pandas(df)
  insert_df.to_gbq(destination_table="{0}.{1}.{2}".format(project_id, bq_dataset, bq_table),
                 if_exists="replace")