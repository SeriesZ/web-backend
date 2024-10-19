import os

from aiokafka import AIOKafkaProducer, AIOKafkaConsumer


async def get_kafka_producer():
    producer = AIOKafkaProducer(
        bootstrap_servers=os.getenv("KAFKA_URL")
    )
    await producer.start()
    return producer


async def get_kafka_consumer(room_id: str):
    consumer = AIOKafkaConsumer(
        room_id,  # Kafka 토픽을 채팅방 room_id로 설정
        bootstrap_servers=os.getenv("KAFKA_URL"),
        group_id=f"group_{room_id}"  # 컨슈머 그룹 ID 설정 (각 방마다 별도의 그룹)
    )
    await consumer.start()
    return consumer
