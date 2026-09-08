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


def find_route(collection, route_short_name):
    """Recherche une ligne de transport par son nom court."""
    route = collection.find_one(
        {"route_short_name": route_short_name},
        {"_id": 0},
    )

    logger.info(
        "Recherche de la ligne '%s' : %s",
        route_short_name,
        route,
    )

    return route


def aggregate_stops_by_route(collection):
    """Compte le nombre d'arrêts pour chaque ligne de transport."""
    pipeline = [
        {
            "$project": {
                "_id": 0,
                "route_short_name": 1,
                "stop_count": {"$size": "$stops"},
            }
        }
    ]

    results = list(collection.aggregate(pipeline))

    logger.info(
        "Nombre d'arrêts par ligne : %s",
        results,
    )

    return results


def load_documents(
    mongo_client,
    database_name,
    collection_name,
    documents,
):
    """Charge des documents dans une collection MongoDB."""
    collection = mongo_client[database_name][collection_name]

    collection.delete_many({})

    result = collection.insert_many(documents)

    logger.info(
        "%s documents chargés dans la collection '%s'",
        len(result.inserted_ids),
        collection_name,
    )
