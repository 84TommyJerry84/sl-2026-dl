import logging

import duckdb

logger = logging.getLogger(__name__)


def aggregate_stops(input_path, output_path):
    """Agrège le nombre d'arrêts par ligne et écrit un fichier Parquet."""
    connection = duckdb.connect()

    try:
        connection.execute(
            f"""
            COPY (
                SELECT
                    line_name,
                    COUNT(DISTINCT stop_id) AS stop_count
                FROM read_parquet('{input_path}')
                WHERE line_name IS NOT NULL
                AND stop_id IS NOT NULL
                GROUP BY line_name
                ORDER BY line_name
            )
            TO '{output_path}'
            (FORMAT PARQUET)
            """
        )

        logger.info(
            "Le fichier curated a été créé : %s",
            output_path,
        )
    finally:
        connection.close()
