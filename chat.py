'''
Functionality to enable chat using Redis and web sockets
'''
from app import sockets, redis, gevent


# Name the channel
REDIS_CHAN = 'chat'


'''
ChatBackend() initializes a chat web socket. It uses REDIS_CHAN as the name of the channel
'''
class ChatBackend(object):

    # Initialize the class
    def __init__(self):
        self.clients = list()
        self.pubsub = redis.pubsub() # Assign Redis pubsub() to class-callable method
        self.pubsub.subscribe(REDIS_CHAN) # Subscribe to channel

    #Iterate over the message submitted to the channel
    def __iter_data(self):
        for message in self.pubsub.listen():
            data = message.get('data')
            if message['type'] == 'message':
                yield data

    # Register a client to a channel
    def register(self, client):
        self.clients.append(client)

    # Send a message to a channel
    def send(self, client, data):
        try: # Try to send the message
            client.send(data)
        except Exception: #Remove the client from the channel if message-sending fails
            self.clients.remove(client)

    # Start a gevent>greenlet thread for asynchronous data exchange
    def run(self):
        for data in self.__iter_data():
            for client in self.clients:
                gevent.spawn(self.send, client, data)

    # Start the communication thread
    def start(self):
        gevent.spawn(self.run)


# Initialize a new communication pool
chat = ChatBackend()
chat.start()


# Route for submitting a chat message
@sockets.route('/submit_chat')
def inbox(ws):
    while not ws.closed:  # Keep the socket alive
        gevent.sleep(0.1)
        message = ws.receive()

        if message:
            redis.publish(REDIS_CHAN, message)


# Route for receiving a chat message
@sockets.route('/receive_chat')
def outbox(ws):
    chat.register(ws)  # Register the web socket
    while not ws.closed:
        gevent.sleep(0.1)
