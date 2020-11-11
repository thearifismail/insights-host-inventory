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
        print("type(event):", type(event))
        print("event:", event)

        event_dict = json.loads(event)
        # event_dict = [2, 3, 4, 5]
        logger.info(f"{event}")
        repo       = "/Users/aarif/Documents/dev-ws/insights/inventory-schemas"
        path       = "schemas/system_profile/v1.yaml"
        new_sr     = SchemaRepo(repo, "hackathon", path)
        new_schema = new_sr.get_schema()
        print("New schema:")
        print(f"{new_schema}")

        try:
            print("Checking using new branch...")
            jsonschema_validate(event_dict, new_schema)
        except Exception as ex:
            print (f"some error: {ex}")

        master_sr  =  SchemaRepo(repo, "master", path)
        master_schema = master_sr.get_schema()
        print("Master schema: ")
        print(f"{master_schema}")
        osv = jsonschema_validate(event_dict, master_schema)

        try:
            print("Checking using master branch ...")
            jsonschema_validate(event_dict, master_schema)
        except Exception as ex:
            print (f"some error: {ex}")

        print(f"New schema validation: {nsv}")
        print(f"Old schema validation: {osv}")


    def close(self):
        self._kafka_consumer.close()
