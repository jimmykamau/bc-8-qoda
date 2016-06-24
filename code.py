'''
Functionality to enable real-time code submission
'''
from app import sockets, redis, gevent


# Channel's name
REDIS_CHAN = 'code'


'''
CodeBackend() initializes a code-submission \
web socket. It uses REDIS_CHAN as the channel's name
'''


class CodeBackend(object):

    # Initialize class
    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub()  # Assign Redis' pubsub() method to a class method
        self.pubsub.subscribe(REDIS_CHAN)  # Subscribe to channel

    # Iterate over message submitted to channel
    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                yield data

    # Register a client to the channel
    def register(self, client):
        self.clients.append(client)

    # Send a message to the channel
    def send(self, client, data):
        try:  # Try to send the message
            client.send(data)
        except Exception:  # If sending message fails, remove the client from the channel
            self.clients.remove(client)

    # Start a gevent>greenlet thread for asynchronous data exchange
    def run(self):
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    # Start communication thread
    def start(self):
        gevent.spawn(self.run)


# Initialize communication pool
code = CodeBackend()
code.start()


# Route for submitting code
@sockets.route('/submit')
def inbox(ws):
    while not ws.closed:  # Keep the socket alive
        gevent.sleep(0.1)
        message = ws.receive()

        if message:
            redis.publish(REDIS_CHAN, message)


# Route for receiving code
@sockets.route('/receive')
def outbox(ws):
    code.register(ws)  # Register the web socket
    while not ws.closed:
        gevent.sleep(0.1)
