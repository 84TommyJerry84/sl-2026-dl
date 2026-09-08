import os

from src.logging_config import logger, measure_time
from src.minio_client import (
    create_s3_client,
    ensure_bucket,
    read_object,
    upload_file,
)
from src.mongo_client import (
    aggregate_stops_by_route,
    create_mongo_client,
    find_route,
    load_json_documents,
)


def main():
    """Exécute la partie 1 et dépose le Parquet dans la zone raw."""
    bucket_name = os.environ["MINIO_BUCKET"]
    file_path = os.environ["MINIO_TEST_FILE"]
    object_name = os.environ["MINIO_TEST_OBJECT"]

    raw_bucket = os.environ["MINIO_RAW_BUCKET"]
    curated_bucket = os.environ["MINIO_CURATED_BUCKET"]
    raw_object = os.environ["MINIO_RAW_OBJECT"]

    mongo_database = os.environ["MONGO_DATABASE"]
    mongo_collection = os.environ["MONGO_COLLECTION"]
    mongo_json_file = os.environ["MONGO_JSON_FILE"]

    s3_client = create_s3_client()

    try:
        ensure_bucket(s3_client, bucket_name)
        ensure_bucket(s3_client, raw_bucket)
        ensure_bucket(s3_client, curated_bucket)

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

        upload_file(
            s3_client,
            raw_bucket,
            file_path,
            raw_object,
        )
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

        collection = mongo_client[mongo_database][mongo_collection]

        find_route(collection, "T3a")

        aggregate_stops_by_route(collection)
    finally:
        mongo_client.close()


if __name__ == "__main__":
    measure_time(main)
