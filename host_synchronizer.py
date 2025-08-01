#!/usr/bin/python
import sys
from functools import partial

from prometheus_client import CollectorRegistry
from prometheus_client import push_to_gateway
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app import create_app
from app.config import Config
from app.environment import RuntimeEnvironment
from app.logging import configure_logging
from app.logging import get_logger
from app.logging import threadctx
from app.models import Host
from app.models import Staleness
from app.queue.event_producer import create_event_producer
from app.queue.metrics import event_producer_failure
from app.queue.metrics import event_producer_success
from app.queue.metrics import event_serialization_time
from lib.db import session_guard
from lib.handlers import ShutdownHandler
from lib.handlers import register_shutdown
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

application = create_app(RUNTIME_ENVIRONMENT)
app = application.app


def _init_config():
    config = Config(RUNTIME_ENVIRONMENT)
    config.log_configuration()
    return config


def _init_db(config):
    engine = create_engine(config.db_uri)
    return sessionmaker(bind=engine)


def _prometheus_job(namespace):
    return f"{PROMETHEUS_JOB}-{namespace}" if namespace else PROMETHEUS_JOB


def _excepthook(logger, type, value, traceback):  # noqa: ARG001, needed by sys.excepthook
    logger.exception("Host synchronizer failed", exc_info=value)


@synchronize_fail_count.count_exceptions()
def run(config, logger, session, event_producer, shutdown_handler):
    query_hosts = session.query(Host)
    query_staleness = session.query(Staleness)
    update_count = synchronize_hosts(
        query_hosts, query_staleness, event_producer, config.script_chunk_size, config, shutdown_handler.shut_down
    )
    logger.info(f"Total number of hosts synchronized: {update_count}")
    return update_count


def main(logger):
    config = _init_config()
    registry = CollectorRegistry()

    for metric in COLLECTED_METRICS:
        registry.register(metric)

    job = _prometheus_job(config.kubernetes_namespace)
    prometheus_shutdown = partial(push_to_gateway, config.prometheus_pushgateway, job, registry)
    register_shutdown(prometheus_shutdown, "Pushing metrics")

    Session = _init_db(config)
    session = Session()
    register_shutdown(session.get_bind().dispose, "Closing database")

    event_producer = create_event_producer(config, config.event_topic)
    register_shutdown(event_producer.close, "Closing producer")

    shutdown_handler = ShutdownHandler()
    shutdown_handler.register()

    with session_guard(session), app.app_context():
        run(config, logger, session, event_producer, shutdown_handler)


if __name__ == "__main__":
    configure_logging()

    logger = get_logger(LOGGER_NAME)
    sys.excepthook = partial(_excepthook, logger)

    threadctx.request_id = None
    main(logger)
