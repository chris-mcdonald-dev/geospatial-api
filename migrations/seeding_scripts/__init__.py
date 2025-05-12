import pandas as pd
import geopandas as gpd
from geoalchemy2.shape import from_shape
import shapely.geometry
import json
from app.db import get_db_for_alembic
from app.models import Link, SpeedRecord
import time

def seed_db(bind):
  # Read data files
  link_info_file = "datasets/link_info.parquet.gz"
  speed_data_file = "datasets/duval_jan1_2024.parquet.gz"

  print(f"Reading {link_info_file}...")
  link_df = pd.read_parquet(link_info_file)
  print(f"Finished reading {link_info_file}. Rows: {len(link_df)}")

  try:
    # Convert to GeoJSON
    link_df['geometry'] = link_df['geo_json'].apply(
        lambda row: shapely.geometry.shape(json.loads(row))
    )

  except Exception as e:
    print(f"Error parsing geo_json column: {e}")

  print(f"Reading {speed_data_file}...")
  speed_df = pd.read_parquet(speed_data_file)
  print(f"Finished reading {speed_data_file}. Rows: {len(speed_df)}")

  # Add to the database
  try:
    with get_db_for_alembic(bind=bind) as db:
      print("Starting Link ingestion...")
      all_link_objects = [
          Link(
              link_id=row['link_id'],
              length=row['_length'],
              road_name=row['road_name'],
              geometry=from_shape(row['geometry'], srid=4326),
              usdk_speed_category=row['usdk_speed_category'],
              funclass_id=row['funclass_id'],
              speedcat=row['speedcat'],
              volume_value=row['volume_value'],
              volume_bin_id=row['volume_bin_id'],
              volumes_bin_description=row['volumes_bin_description'],
          )
          for index, row in link_df.iterrows()
      ]
      db.add_all(all_link_objects)

      print(f"Link ingestion complete. Added {len(all_link_objects)} objects.")

      #  Ingest Speed Data (optimized with pandas dataframe.tosql() cause the 1.2 million rows was taking 5+ mins with the ORM. Now takes 30-40 seconds)
      db.commit() # Commit the session to save previous changes. Initially was getting foreign key errors since the changes were not committed yet.
      
      print("Starting Speed Record ingestion...")
      start_time = time.time()
      
      speed_df.to_sql(
        name=SpeedRecord.__tablename__,
        con=db.connection(),
        if_exists='append', # Tell pandas not to create a new table
        index=False, # Don't write the DataFrame index as a column
      )
      end_time = time.time()
      print(f"Speed Record ingestion complete. Time taken: {end_time - start_time:.2f} seconds.")

      print("Speed Record ingestion complete.")

  except Exception as e:
    print(f"An error occurred during the seeding process: {e}")

  print("Data ingestion process finished.")