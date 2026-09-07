import logging
import time

file_handler = logging.FileHandler(
    "historique.log",
    encoding="utf-8",
)


file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)


color_handler = logging.StreamHandler()

color_handler.setFormatter(
    logging.Formatter("\033[34m%(asctime)s - %(levelname)s - %(message)s\033[0m")
)


logging.basicConfig(
    level=logging.INFO,
    handlers=[
        file_handler,
        color_handler,
    ],
)

logger = logging.getLogger(__name__)


def measure_time(function):
    """Mesure le temps d'exécution d'une fonction."""
    start = time.perf_counter()

    function()

    end = time.perf_counter()

    logger.info(
        "%s exécutée en %.2f secondes",
        function.__name__,
        end - start,
    )
