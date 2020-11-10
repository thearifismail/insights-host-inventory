from enum import Enum

from kafka import KafkaProducer
from kafka import KafkaConsumer
from kafka.errors import KafkaError

from app.instrumentation import message_not_produced
from app.instrumentation import message_produced
from app.logging import get_logger

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
        print("inside msg_handler()")
        print("type(event):", type(event))
        print("event:", event)

    def close(self):
        self._kafka_consumer.close()
