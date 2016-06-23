from app import sockets, redis, gevent


REDIS_CHAN = 'chat'


class ChatBackend(object):

    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()
        self.pubsub.subscribe(REDIS_CHAN)

    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                yield data

    def register(self, client):
        self.clients.append(client)

    def send(self, client, data):
        try:
            client.send(data)
        except Exception:
            self.clients.remove(client)

    def run(self):
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    def start(self):
        gevent.spawn(self.run)


chat = ChatBackend()
chat.start()


@sockets.route('/submit_chat')
def inbox(ws):
    while not ws.closed:
        gevent.sleep(0.1)
        message = ws.receive()

        if message:
            redis.publish(REDIS_CHAN, message)


@sockets.route('/receive_chat')
def outbox(ws):
    chat.register(ws)
    while not ws.closed:
        gevent.sleep(0.1)
