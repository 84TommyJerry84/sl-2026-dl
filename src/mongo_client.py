import json
import logging
import os

from pymongo import MongoClient

logger = logging.getLogger(__name__)


def create_mongo_client():
    """Crée et retourne un client MongoDB configuré avec les variables d'environnement."""
    return MongoClient(
        os.environ["MONGO_ENDPOINT"],
        username=os.environ["MONGO_ROOT_USER"],
        password=os.environ["MONGO_ROOT_PASSWORD"],
        authSource="admin",
    )


def load_json_documents(
    mongo_client,
    database_name,
    collection_name,
    file_path,
):
    """Charge les documents d'un fichier JSON dans une collection MongoDB."""
    with open(file_path, "r", encoding="utf-8") as file:
        documents = json.load(file)

    collection = mongo_client[database_name][collection_name]

    collection.delete_many({})

    result = collection.insert_many(documents)

    logger.info(
        "%s documents chargés dans la collection '%s'",
        len(result.inserted_ids),
        collection_name,
    )
