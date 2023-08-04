import asyncio
import datetime

import bcrypt
import jwt
import msgpack
import websockets
from redis_connection import Redis


async def echo(websocket):
    try:
        async for message in websocket:
            # Echo back the received message
            # print(websocket.id)
            message = msgpack.unpackb(message)

            # Process the message
            response = await process_message(message)
            print(response)

            try:
                await websocket.send(response)
            except websockets.exceptions.ConnectionClosedOK:
                print("Client disconnected.")
    except websockets.exceptions.ConnectionClosedOK:
        print("Connection closed gracefully.")
    except Exception as e:
        print(e)


async def create_jwt(username: str):
    # Create a payload with the username as a claim
    payload = {
        "username": username,
        "exp": datetime.datetime.utcnow()
        + datetime.timedelta(hours=1),  # Token expiration time (adjust as needed)
    }

    # Create the JWT token
    token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")

    return token


async def process_message(message: dict):
    # Check if the message is a login request
    if message["kind"] == "login":
        # Unpack the username and password
        username = message["data"]["username"]
        password = message["data"]["password"]

        # Authenticate the user
        if await authenticate(username, password):
            return await create_jwt(username)
        else:
            return "Invalid username or password"
    # Check if the message is a register request
    elif message["kind"] == "register":
        # Unpack the username and password
        username = message["data"]["username"]
        password = message["data"]["password"]

        # Register the user
        if await register_user(username, password):
            return await create_jwt(username)
        else:
            return "Username already exists!"
    elif message["kind"] == "message":
        response = await process_text_message(message)
        return response


async def process_text_message(message: dict):
    # Check if the user is logged in
    if "jwt_token" not in message["data"]:
        return "You must be logged in to send messages!"

    # Check if the JWT is valid
    if not await check_jwt(message["data"]["jwt_token"]):
        return "Invalid JWT!"

    # Unpack the message
    message = message["data"]["message"]

    # Send the message to all connected clients
    return message


async def check_jwt(token: str):
    # Decode the JWT token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    except jwt.exceptions.InvalidSignatureError:
        return False

    # Get the current time in UTC as an offset-aware datetime object
    current_time_utc = datetime.datetime.now()
    # Check if the token has expired
    if current_time_utc < datetime.datetime.utcfromtimestamp(payload["exp"]):
        return False

    if not redis.exists(payload["username"]):
        return False

    return True


async def authenticate(username: str, password: str):
    # Check if the username exists
    if not redis.exists(username):
        return False

    # Get the user's hashed password
    hashed_password = redis.hget(username, "password")

    # Check if the password is correct
    if check_password(password, hashed_password) is False:
        return "Invalid username or password"

    return "Successfully logged in!"


def check_password(password, hashed_password):
    # Check if the provided password matches the hashed password
    # Do not use this in production!
    fixed_salt = b"$2b$12$8Kaf.XtoDeK5ZN.LUfcz/O"

    return bcrypt.checkpw(
        hashed_password, bcrypt.hashpw(password.encode("utf-8"), fixed_salt)
    )


async def register_user(username: str, password: str):
    # Check if the username exists
    if redis.exists(username):
        return False

    # Register the user
    redis.hset(username, "password", password)

    return True


# Connect to Redis
redis = Redis(
    host="localhost",
    port=6379,
)

# Replace this with your secret key. Keep this secure and do not hardcode it in production.
SECRET_KEY = "super-secret-key"


# Start the WebSocket server
start_server = websockets.serve(echo, "localhost", 8765)

# Run the event loop to keep the server running
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
