from enum import Enum
import json

from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from app.instrumentation import message_not_produced
from app.instrumentation import message_produced
from app.logging import get_logger

from lib.schema_repository import SchemaRepository as SchemaRepo

from jsonschema import validate as jsonschema_validate

from app.serialization import deserialize_host_mq
from yaml import safe_load as yaml_safe_load

from app.exceptions import ValidationException

logger = get_logger(__name__)

Topic = Enum("Topic", ("ingress", "events"))

class EventConsumer:
    def __init__(self, config):
        logger.info("Starting EventConsumer()")
        self._kafka_consumer = KafkaConsumer(**config.kafka_consumer, group_id=config.host_ingress_consumer_group, bootstrap_servers=config.bootstrap_servers)
        self.topics = {Topic.ingress: config.host_ingress_topic, Topic.events: config.event_topic}


    def msg_handler(self, event, key, headers, topic, *, wait=False):
        # TODO: 
        #   1.  what's the structure of message from Kafkaa
        #   2.  connect to inventory schema repo and check out schema
        #       https://github.com/RedHatInsights/insights-host-inventory has
        #       only system-profile schema.  Which schema should we validate
        #       against.
        #   3.  # TODO: is libgit2 needed?  When tried "pip search libgit2", it returned "pygit2"
        #               and that's what I included in Pipfile.
        print("inside msg_handler()")

        host_dict  = json.loads(event)
        sp         = host_dict["host"]["system_profile"]
        repo       = "/Users/aarif/Documents/dev-ws/insights/inventory-schemas"
        path       = "schemas/system_profile/v1.yaml"

        schema_path = "/Users/aarif/Documents/dev-ws/insights/insights-host-inventory/swagger/system_profile.spec.yaml"
        schema_dict = yaml_safe_load(open(schema_path))
        good_schema = {**schema_dict, "$ref": "#/$defs/SystemProfile"}

        try:
            jsonschema_validate(sp, good_schema)
            print("Successfully validated system-profile schema in new branch")
        except Exception as ex:
            print ("Problem validating system-profile schema in new branch")
            print (f"some error: {ex}")

        master_sr     =  SchemaRepo(repo, "master", path)
        master_schema = master_sr.get_schema()
        good_master   = {**master_schema, "$ref": "#/$defs/SystemProfile"}

        try:
            print("Checking using master branch ...")
            jsonschema_validate(sp, good_master)
            print("Successfully validated system-profile schema in Master branch")
        except Exception as ex:
            print ("Problem validating system-profile schema in Master branch")
            print (f"some error: {ex}")


    def close(self):
        self._kafka_consumer.close()
