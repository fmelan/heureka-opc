from json import loads

import structlog
from aiokafka import AIOKafkaConsumer
from aiokafka.helpers import create_ssl_context

from settings import settings

log = structlog.get_logger()


async def read_kafka_messages(msg_processor):
    """
    Reads messages from kafka and process them using the
    calls of the passed function.
    :param msg_processor: function for processing the messages
    :return:
    """
    consumer = AIOKafkaConsumer(
        settings.topic,
        bootstrap_servers=[settings.bootstrap_servers],
        security_protocol=settings.security_protocol,
        ssl_context=create_ssl_context(),
        sasl_plain_username=settings.sasl_plain_username,
        sasl_plain_password=settings.sasl_plain_password,
        sasl_mechanism=settings.sasl_mechanism,
        auto_offset_reset=settings.auto_offset_reset,
        enable_auto_commit=settings.enable_auto_commit,
        value_deserializer=lambda x: loads(x.decode("utf-8")),
    )
    await consumer.start()
    try:
        async for msg in consumer:
            log.info("Message from kafka: ", message=msg.value)
            msg_processor(msg.value["payload"])
            log.info("Message processed.")
    finally:
        await consumer.stop()
