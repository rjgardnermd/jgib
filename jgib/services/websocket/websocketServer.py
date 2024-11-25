import asyncio
import websockets


class WebSocketServer:
    def __init__(self):
        self.connected_clients = set()

    async def handle_client(self, websocket):
        # Add client to the set of connected clients
        self.connected_clients.add(websocket)
        print(f"New client connected: {websocket.remote_address}")

        try:
            async for message in websocket:
                print(f"Received message from {websocket.remote_address}: {message}")
                # Broadcast the message to all connected clients
                for client in self.connected_clients:
                    if client != websocket:  # Avoid echoing back to the sender
                        await client.send(
                            f"Client {websocket.remote_address} says: {message}"
                        )
        except websockets.exceptions.ConnectionClosed as e:
            print(f"Client disconnected: {websocket.remote_address}")
        finally:
            # Remove client from the set of connected clients
            self.connected_clients.remove(websocket)

    # Start the WebSocket server
    async def start(self, host, port):
        server = await websockets.serve(self.handle_client, host, port)
        print(f"WebSocket server started on ws://{host}:{port}")
        await server.wait_closed()


if __name__ == "__main__":
    # Run the server
    server = WebSocketServer()
    asyncio.run(server.start("localhost", 8765))

# server = WebSocketServer()
# asyncio.run(server.start("localhost", 8765))
# asyncio.run(main())
