import asyncio
import os

import bcrypt
import msgpack
import pyfiglet
import websockets
from redis_connection import Redis


async def receive_messages(websocket):
    try:
        while True:
            response = await websocket.recv()
            print("Server:", response)
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection to server closed.")


async def send_messages():
    # Display the welcome message
    await display_welcome()

    # Initialize websocket
    async with websockets.connect("ws://localhost:8765", timeout=1000) as websocket:
        # Login or register an account
        username = await login_register(websocket)

        # Connect to the WebSocket server
        if redis.hexists("jwt", str(websocket.id)):
            while True:
                # Capture the user's input
                await send_text_message(websocket)

                response = await websocket.recv()
                print(f"{username}:", response)


async def display_welcome():
    # Generate ASCII art for "Streamline"
    ascii_art = pyfiglet.figlet_format("streamline")
    print(ascii_art)


async def login_register(websocket: websockets.WebSocketClientProtocol):
    # Check if the user wants to login or register an account
    print("1. Login")
    print("2. Register")
    choice = input("> ")

    # If the user wants to login, request their username and password
    if choice == "1":
        return await request_login(websocket)
    # If the user wants to register, request their username and password
    elif choice == "2":
        return await request_register(websocket)


async def send_text_message(websocket: websockets.WebSocketClientProtocol):
    # Capture the user's input
    message = input("> ")

    # If the user wants to exit, send the exit message
    if message.lower() == "exit":
        os._exit(0)

    # Pack the message into a MessagePack object
    kind = "message"
    data = {"message": message}

    # Include the JWT in the message if the user is logged in
    data["jwt_token"] = redis.hget("jwt", str(websocket.id))
    # print(redis.hget("jwt", str(websocket.id)))

    packed_data = msgpack.packb({"kind": kind, "data": data})

    # Send the message to the server
    response = await websocket.send(packed_data)

    if response == "You must be logged in to send messages!":
        print("You must be logged in to send messages!")
        await exit_client(websocket)
    elif response == "Invalid JWT!":
        print("Invalid JWT!")
        await exit_client(websocket)
    else:
        return response


async def request_login(websocket: websockets.WebSocketClientProtocol):
    # Request the user's username and password
    username = input("Username: ")
    password = input("Password: ")

    # Hash the password
    hashed_password = hash_password(password)

    # Pack the username and password into a MessagePack object
    kind = "login"
    data = {"username": username, "password": hashed_password}
    packed_data = msgpack.packb({"kind": kind, "data": data})

    # Send the username and password to the server
    await websocket.send(packed_data)
    response = await websocket.recv()

    if response == "Invalid username or password!":
        print("Invalid username or password!")
        await exit_client(websocket)
    else:
        print("Successfully logged in!")
        # Store the user's JWT
        await set_jwt(websocket.id, response)

        return username


def hash_password(password):
    # Generate a salt and hash the password
    # Do not use this salt in production!
    fixed_salt = b"$2b$12$8Kaf.XtoDeK5ZN.LUfcz/O"
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), fixed_salt)

    return hashed_password.decode("utf-8")


async def request_register(websocket: websockets.WebSocketClientProtocol):
    # Request the user's username and password
    username = input("Username: ")
    password = input("Password: ")

    # Hash the password
    hashed_password = hash_password(password)

    # Pack the username and password into a MessagePack object
    kind = "register"
    data = {"username": username, "password": hashed_password}
    packed_data = msgpack.packb({"kind": kind, "data": data})

    # Send the username and password to the server
    await websocket.send(packed_data)
    response = await websocket.recv()

    if response != "Username already exists!":
        print("Successfully registered!")
        # Store the user's JWT
        await set_jwt(websocket.id, response)

        return username
    else:
        print("Username already exists!")
        await exit_client(websocket)


async def set_jwt(websocket_id, jwt_token):
    # Set the token in Redis
    redis.hset("jwt", str(websocket_id), str(jwt_token))

    # Output the JWT
    print(redis.hget("jwt", str(websocket_id)))


async def exit_client(websocket: websockets.WebSocketClientProtocol):
    # Unset the JWT environment variable
    redis.hdel("jwt", str(websocket.id))

    # Close the WebSocket connection
    await websocket.close()


# Connect to Redis
redis = Redis(
    host="localhost",
    port=6380,
)

# Run the WebSocket client
asyncio.get_event_loop().run_until_complete(send_messages())
