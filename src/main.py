import os

from src.logging_config import logger, measure_time
from src.minio_client import (
    create_s3_client,
    ensure_bucket,
    read_object,
    upload_file,
)


def main():
    """Run the MinIO discovery workflow."""
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

        logger.info(f"Contenu de l'objet : {content.decode('utf-8')}")
    finally:
        s3_client.close()


if __name__ == "__main__":
    measure_time(main)
