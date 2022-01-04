class WebSocket:
    def __init__(self) -> None:
        self.type = "Websocket"
        self.status = False

    def accept(self):
        self.status = True

    def send_text(self, string):
        return string
