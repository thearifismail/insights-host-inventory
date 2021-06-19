import logging
import os

import payloads
from kafka import KafkaProducer
from ttictoc import TicToc

# When using Clowder, set the KAFKA_HOST_INGRESS_TOPIC to topicName.evn.ns
# e.g. "KAFKA_HOST_INGRESS_TOPIC", "platform.inventory.host-ingress.env-$NS.$NS"
# where NS=<NAMESPACE>
# HOST_INGRESS_TOPIC = os.environ.get("KAFKA_HOST_INGRESS_TOPIC", \
# "platform.inventory.host-ingress.env-ephemeral-07.ephemeral-07")
HOST_INGRESS_TOPIC = os.environ.get("KAFKA_HOST_INGRESS_TOPIC", "platform.inventory.host-ingress")
BOOTSTRAP_SERVERS = os.environ.get("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
NUM_HOSTS = int(os.environ.get("NUM_HOSTS", 5))


def main():
    # Create list of host payloads to add to the message queue
    # payloads.build_payloads takes two optional args: number of hosts, and payload type ("default", "rhsm", "qpc")
    with TicToc("Build payloads"):
        all_payloads = [payloads.build_mq_payload() for _ in range(NUM_HOSTS)]
    print("Number of hosts (payloads): ", len(all_payloads))

    producer = KafkaProducer(bootstrap_servers=BOOTSTRAP_SERVERS, api_version=(0, 10))
    print("HOST_INGRESS_TOPIC:", HOST_INGRESS_TOPIC)

    with TicToc("Send all hosts to queue"):
        for payload in all_payloads:
            producer.send(HOST_INGRESS_TOPIC, value=payload)
    producer.flush()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    main()
