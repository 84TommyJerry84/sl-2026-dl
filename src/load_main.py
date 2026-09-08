import os

from src.load_curated import read_curated_parquet
from src.logging_config import measure_time
from src.minio_client import create_s3_client, download_file
from src.mongo_client import create_mongo_client, load_documents


def main():
    """Charge les données curated dans MongoDB."""
    curated_bucket = os.environ["MINIO_CURATED_BUCKET"]
    curated_object = os.environ["MINIO_CURATED_OBJECT"]

    database_name = os.environ["MONGO_DATABASE"]
    collection_name = os.environ["MONGO_CURATED_COLLECTION"]

    curated_path = "/tmp/curated.parquet"

    s3_client = create_s3_client()

    try:
        download_file(
            s3_client,
            curated_bucket,
            curated_object,
            curated_path,
        )
    finally:
        s3_client.close()

    documents = read_curated_parquet(curated_path)

    mongo_client = create_mongo_client()

    try:
        load_documents(
            mongo_client,
            database_name,
            collection_name,
            documents,
        )
    finally:
        mongo_client.close()


if __name__ == "__main__":
    measure_time(main)
