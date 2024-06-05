from confluent_kafka import Producer, Consumer, KafkaError

class KafkaProducer:
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.producer = Producer({'bootstrap.servers': bootstrap_servers})

    def send_message(self, message, topic='my_topic'):
        self.producer.produce(topic, message.encode('utf-8'))
        self.producer.flush()

class KafkaConsumer:
    def __init__(self, bootstrap_servers='localhost:9092', group_id='my_group'):
        self.consumer = Consumer({
            'bootstrap.servers': bootstrap_servers,
            'group.id': group_id,
            'auto.offset.reset': 'earliest'
        })
        self.consumer.subscribe(['my_topic'])

    def receive_message(self):
        msg = self.consumer.poll(timeout=1.0)
        if msg is None:
            return "No messages available"
        elif not msg.error():
            return msg.value().decode('utf-8')
        elif msg.error().code() == KafkaError._PARTITION_EOF:
            return "End of partition reached"
        else:
            return f"Error: {msg.error().str()}"
