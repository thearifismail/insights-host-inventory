import sys
from ctypes import sizeof
from functools import partial

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import Config
from app.environment import RuntimeEnvironment
from app.logging import configure_logging
from app.logging import get_logger
from app.logging import threadctx
from app.models import Host
from app.queue.metrics import event_producer_failure
from app.queue.metrics import event_producer_success
from app.queue.metrics import event_serialization_time
from lib.host_synchronize import synchronize_hosts
from lib.metrics import synchronize_fail_count
from lib.metrics import synchronize_host_count

__all__ = ("main", "run")

PROMETHEUS_JOB = "inventory-synchronizer"
LOGGER_NAME = "inventory_synchronizer"
COLLECTED_METRICS = (
    synchronize_host_count,
    synchronize_fail_count,
    event_producer_failure,
    event_producer_success,
    event_serialization_time,
)
RUNTIME_ENVIRONMENT = RuntimeEnvironment.JOB


def _init_config():
    config = Config(RUNTIME_ENVIRONMENT)
    config.log_configuration()
    return config


def _init_db(config):
    engine = create_engine(config.db_uri)
    return sessionmaker(bind=engine)


def _excepthook(logger, type, value, traceback):
    logger.exception("Host synchronizer failed", exc_info=value)


@synchronize_fail_count.count_exceptions()
def run(config, logger, session, event_producer, shutdown_handler):
    query = session.query(Host)

    update_count = synchronize_hosts(
        query, event_producer, config.script_chunk_size, config, shutdown_handler.shut_down
    )
    logger.info("Total number of hosts synchronized: {update_count}")
    return update_count


def main(logger):
    config = _init_config()
    Session = _init_db(config)
    session = Session()

    result = session.execute(
        "SELECT COUNT(*) \
        FROM hosts \
        WHERE LEFT(id::text, 1) = '1'"
    )
    cursor = result.cursor
    records = cursor.fetchmany(5)
    print("Number of hosts with id starting with '1': {records[0][0]}")
    print(sizeof.asized(records, detail=1).format())


if __name__ == "__main__":
    configure_logging()

    logger = get_logger(LOGGER_NAME)
    sys.excepthook = partial(_excepthook, logger)

    threadctx.request_id = None
    main(logger)
