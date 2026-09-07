import logging
import time

logger = logging.getLogger(__name__)

logging.basicConfig(
    filename="historique.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)


def measure_time(function):
    """Exécute une fonction et affiche son temps d'exécution."""
    start = time.time()

    function()

    end = time.time()

    logger.info(f"{function.__name__} exécutée en {end - start:.2f} secondes")
