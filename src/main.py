import os

from src.logging_config import logger, measure_time
from src.minio_client import (
    create_s3_client,
    ensure_bucket,
    read_object,
    upload_file,
)
from src.mongo_client import create_mongo_client, load_json_documents

mongo_database = os.environ["MONGO_DATABASE"]
mongo_collection = os.environ["MONGO_COLLECTION"]
mongo_json_file = os.environ["MONGO_JSON_FILE"]


def main():
    """Exécute le workflow de découverte de MinIO."""
    bucket_name = os.environ["MINIO_BUCKET"]
    file_path = os.environ["MINIO_TEST_FILE"]
    object_name = os.environ["MINIO_TEST_OBJECT"]

    s3_client = create_s3_client()

    try:
        ensure_bucket(s3_client, bucket_name)

        upload_file(
            s3_client,
            bucket_name,
            file_path,
            object_name,
        )

        content = read_object(
            s3_client,
            bucket_name,
            object_name,
        )

        logger.info("Objet relu : %s octets", len(content))
    finally:
        s3_client.close()

    mongo_client = create_mongo_client()

    try:
        load_json_documents(
            mongo_client,
            mongo_database,
            mongo_collection,
            mongo_json_file,
        )
    finally:
        mongo_client.close()


if __name__ == "__main__":
    measure_time(main)
