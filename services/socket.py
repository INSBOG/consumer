import socketio
import os

SOCKET_URI = os.getenv("SOCKET_URI")

class SocketService:
    def __init__(self):
        self.sio = socketio.Client()
        self.connect_socket()

    def connect_socket(self):
        try:
            print("Connecting to socket...")
            self.sio.connect(SOCKET_URI, transports=["websocket"])
        except Exception as e:
            print("Error:", str(e))

    def emit(self, event, data):
        try:
            self.sio.emit(event, data)
        except Exception as e:
            print("Error:", str(e))

    def on(self, event, callback):
        self.sio.on(event, callback)

    def disconnect_socket(self):
        try:
            self.sio.disconnect()
        except Exception as e:
            print("Error:", str(e))
