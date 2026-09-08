import logging

import duckdb

logger = logging.getLogger(__name__)


def read_curated_parquet(file_path):
    """Lit le fichier curated et retourne des documents Python."""
    connection = duckdb.connect()

    try:
        rows = connection.execute(
            f"""
            SELECT
                line_name,
                stop_count
            FROM read_parquet('{file_path}')
            """
        ).fetchall()
    finally:
        connection.close()

    documents = [
        {
            "line_name": line_name,
            "stop_count": stop_count,
        }
        for line_name, stop_count in rows
    ]

    logger.info(
        "%s documents lus depuis le fichier curated",
        len(documents),
    )

    return documents
