import logging
import os

import boto3
from botocore.exceptions import ClientError

logger = logging.getLogger(__name__)


def create_s3_client():
    """Crée et retourne un client S3 configuré pour MinIO."""
    return boto3.client(
        "s3",
        endpoint_url=os.environ["MINIO_ENDPOINT"],
        aws_access_key_id=os.environ["MINIO_ROOT_USER"],
        aws_secret_access_key=os.environ["MINIO_ROOT_PASSWORD"],
    )


def ensure_bucket(s3_client, bucket_name):
    """Crée le bucket s'il n'existe pas déjà."""
    try:
        s3_client.head_bucket(Bucket=bucket_name)
        logger.info("Le bucket '%s' existe déjà", bucket_name)

    except ClientError as error:
        error_code = error.response["Error"]["Code"]

        if error_code in {"404", "NoSuchBucket"}:
            s3_client.create_bucket(Bucket=bucket_name)
            logger.info("Le bucket '%s' a été créé", bucket_name)

        else:
            raise


def upload_file(s3_client, bucket_name, file_path, object_name):
    """Envoie un fichier local dans un bucket MinIO."""
    s3_client.upload_file(
        Filename=file_path,
        Bucket=bucket_name,
        Key=object_name,
    )

    logger.info(
        "Le fichier '%s' a été envoyé dans le bucket '%s' sous le nom '%s'",
        file_path,
        bucket_name,
        object_name,
    )


def download_file(s3_client, bucket_name, object_name, file_path):
    """Télécharge un objet MinIO dans un fichier local."""
    s3_client.download_file(
        Bucket=bucket_name,
        Key=object_name,
        Filename=file_path,
    )

    logger.info(
        "L'objet '%s' a été téléchargé depuis le bucket '%s'",
        object_name,
        bucket_name,
    )


def read_object(s3_client, bucket_name, object_name):
    """Lit un objet depuis un bucket MinIO et retourne son contenu."""
    response = s3_client.get_object(
        Bucket=bucket_name,
        Key=object_name,
    )

    body = response["Body"]

    try:
        content = body.read()
    finally:
        body.close()

    logger.info(
        "L'objet '%s' a été lu depuis le bucket '%s'",
        object_name,
        bucket_name,
    )

    return content
