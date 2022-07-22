import json
from logging import Logger

from flask import g

from app.queue import metrics
from app.queue.metrics import event_producer_failure
from app.queue.metrics import event_producer_success
from app.queue.metrics import rbac_access_denied
from app.queue.metrics import rbac_fetching_failure
from app.queue.metrics import tenant_translator_fetching_failure
from lib.metrics import pendo_fetching_failure


def message_produced(logger, msg):
    value = msg.value().decode("utf-8")
    msg_dict = json.loads(value)

    status = "PRODUCED"
    offset = msg.offset()
    topic = msg.topic()

    key = msg_dict["host"]["id"]
    timestamp = msg_dict["timestamp"]

    # headers fields [('event_type', b'<type>', ('request_id', b'<>'), 'producer', b'<>'), 'insights_id', b'<>')]
    event_type = msg_dict["type"]
    request_id = msg_dict["metadata"]["request_id"]
    insights_id = msg_dict["host"]["insights_id"]
    insights_id = insights_id if insights_id else ""

    headers = [
        ("event_type", event_type.encode("utf-8")),
        ("request_id", request_id.encode("utf-8")),
        # ('producer', b'<>'),
        ("insights_id", insights_id.encode("utf-8")),
    ]

    extra = {"status": status, "offset": offset, "timestamp": timestamp, "topic": topic, "key": key}

    info_extra = {**extra, "headers": headers}
    info_message = f"Message status={status}, offset={offset} timestamp={timestamp} topic=%{topic}, key={key}"
    logger.info(f"{info_message}, extra={info_extra}")

    debug_message = f"Message offset={offset} timestamp={timestamp}] topic={topic} key={key} value={value}"
    debug_extra = {**extra, "value": value}
    logger.debug(debug_message, extra=debug_extra)

    event_producer_success.labels(event_type=event_type, topic=topic).inc()


# def message_not_produced(logger, topic, value, key, headers, error):
# TODO: Does the error object have host info needed to log the failed event for the host.
def message_not_produced(logger, error):
    status = "NOT PRODUCED"
    logger.error(f"Message status={status}, topic={error.egress_topic}, error={str(error)}")

    event_producer_failure.labels(event_type="some_event_producer_error", topic=error.egress_topic).inc()


def get_control_rule():
    if hasattr(g, "access_control_rule"):
        return g.access_control_rule
    else:
        return "None"


# delete host
def log_host_delete_succeeded(logger, host_id, control_rule):
    logger.info("Deleted host: %s", host_id, extra={"access_rule": control_rule})


def log_host_delete_failed(logger, host_id, control_rule):
    logger.info(
        "Hostidentity %s already deleted. Delete event not emitted.", host_id, extra={"access_rule": control_rule}
    )


# get host
def log_get_host_list_succeeded(logger, results_list):
    logger.debug("Found hosts: %s", results_list, extra={"access_rule": get_control_rule()})


def log_get_host_list_failed(logger):
    logger.debug("hosts not found", extra={"access_rule": get_control_rule()})


# get tags
def log_get_tags_succeeded(logger, data):
    logger.debug("Found tags: %s", data, extra={"access_rule": get_control_rule()})


def log_get_tags_failed(logger):
    logger.debug("tags not found", extra={"access_rule": get_control_rule()})


# get sap_system
def log_get_sap_system_succeeded(logger, data):
    logger.debug("Found sap_system: %s", data, extra={"access_rule": get_control_rule()})


def log_get_sap_system_failed(logger):
    logger.debug("sap_system not found", extra={"access_rule": get_control_rule()})


# get sap_sids
def log_get_sap_sids_succeeded(logger, data):
    logger.debug("Found sap_sids: %s", data, extra={"access_rule": get_control_rule()})


def log_get_sap_sids_failed(logger):
    logger.debug("sap_sids not found", extra={"access_rule": get_control_rule()})


# get operating_system
def log_get_operating_system_succeeded(logger, data):
    logger.debug("Found operating_system: %s", data, extra={"access_rule": get_control_rule()})


def log_get_operating_system_failed(logger):
    logger.debug("operating_system not found", extra={"access_rule": get_control_rule()})


# sparse system_profile
def log_get_sparse_system_profile_succeeded(logger, data):
    logger.debug("Found sparse system_profile: %s", data, extra={"access_rule": get_control_rule()})


def log_get_sparse_system_profile_failed(logger):
    logger.debug("Sparse system_profile not found", extra={"access_rule": get_control_rule()})


# add host
def log_add_host_attempt(logger, input_host):
    logger.info(
        "Attempting to add host",
        extra={
            "input_host": {
                "account": input_host.account,
                "org_id": input_host.org_id,
                "display_name": input_host.display_name,
                "canonical_facts": input_host.canonical_facts,
                "reporter": input_host.reporter,
                "stale_timestamp": input_host.stale_timestamp.isoformat(),
                "tags": json.dumps(input_host.tags),
            },
            "access_rule": get_control_rule(),
        },
    )


def log_add_update_host_succeeded(logger, add_result, host_data, output_host):
    metrics.add_host_success.labels(add_result.name, host_data.get("reporter", "null")).inc()  # created vs updated
    # log all the incoming host data except facts and system_profile b/c they can be quite large
    logger.info(
        "Host %s",
        add_result.name,
        extra={
            "host": {i: output_host[i] for i in output_host if i not in ("facts", "system_profile")},
            "access_rule": get_control_rule(),
        },
    )


def log_add_host_failure(logger, message, host_data):
    logger.exception(f"Error adding host: {message} ", extra={"host": host_data})
    metrics.add_host_failure.labels("InventoryException", host_data.get("reporter", "null")).inc()


# update system profile
def log_update_system_profile_success(logger, host_data):
    metrics.update_system_profile_success.inc()
    logger.info("System profile updated for host ID: %s", host_data.get("id"))


def log_update_system_profile_failure(logger, host_data):
    logger.exception("Error updating system profile for host ", extra={"host": host_data})
    metrics.update_system_profile_failure.labels("InventoryException").inc()


# patch host
def log_patch_host_success(logger, host_id_list):
    logger.info("Patched hosts- hosts: %s", host_id_list)


def log_patch_host_failed(logger, host_id_list):
    logger.debug("Failed to find hosts during patch operation - hosts: %s", host_id_list)


def rbac_failure(logger, error_message=None):
    logger.error("Failed to fetch RBAC permissions: %s", error_message)
    rbac_fetching_failure.inc()


def rbac_permission_denied(logger, required_permission, user_permissions):
    logger.debug(
        "Access denied due to RBAC",
        extra={"required_permission": required_permission, "user_permissions": user_permissions},
    )
    rbac_access_denied.labels(required_permission=required_permission).inc()


def tenant_translator_failure(logger: Logger, error_message: str = None):
    logger.error("Failed to access 3scale tenant translator service: %s", error_message)
    tenant_translator_fetching_failure.inc()


def log_db_access_failure(logger, message, host_data):
    logger.error("Failure to access database ", f"{message}")
    metrics.db_communication_error.labels("OperationalError", host_data.get("insights_id", message)).inc()


def pendo_failure(logger, error_message=None):
    logger.error("Failed to send Pendo data: %s", error_message)
    pendo_fetching_failure.inc()
