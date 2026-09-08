import os

from src.logging_config import measure_time
from src.minio_client import (
    create_s3_client,
    download_file,
    upload_file,
)
from src.process_raw import aggregate_stops


def main():
    """Exécute le traitement de la zone raw vers la zone curated."""
    raw_bucket = os.environ["MINIO_RAW_BUCKET"]
    curated_bucket = os.environ["MINIO_CURATED_BUCKET"]
    raw_object = os.environ["MINIO_RAW_OBJECT"]
    curated_object = os.environ["MINIO_CURATED_OBJECT"]

    raw_path = "/tmp/raw.parquet"
    curated_path = "/tmp/curated.parquet"

    s3_client = create_s3_client()

    try:
        download_file(
            s3_client,
            raw_bucket,
            raw_object,
            raw_path,
        )

        aggregate_stops(
            raw_path,
            curated_path,
        )

        upload_file(
            s3_client,
            curated_bucket,
            curated_path,
            curated_object,
        )
    finally:
        s3_client.close()


if __name__ == "__main__":
    measure_time(main)
