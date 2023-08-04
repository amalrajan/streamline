<h1 align="center">Streamline</h1>

<p align="center">
  Streamline is an echo server built using websockets. It can be extended to build real-time chat applications.
</p>

## Table of Contents

- [Flow Diagram](#flow-diagram)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)

## Flow Diagram
![Flow Diagram](https://ik.imagekit.io/5jrct2yttdr/streamline_JCEo0RI7S.png?updatedAt=1691183047295)

## Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/amalrajan/streamline.git
   cd jottr
   ```

2. Install the dependencies:

   ```bash
   python -m pip install -r requirements.txt
   ```


## Usage

1. Running the Server: 

    To run the server, execute the following command:

    ```bash
    python server.py
    ```
    The server will start running on http://localhost:8765.

    To test the server, open a new terminal and run the following command:

    ```bash
    python client.py
    ```

2. Authentication

    JWT (JSON Web Token) authentication is used to secure the Streamline application. Upon successful login, users receive a JWT token that contains encoded user information. This token is sent with subsequent requests to authenticate and authorize access to protected routes, ensuring a secure and stateless authentication process.

3. Database

    First, open a terminal or command prompt and run the following command to pull the official Redis Docker image from Docker Hub:

    ```bash
    docker pull redis:latest
    ```

    Now, start a new Redis container using the docker run command.

    ```bash
    docker run --name redis -p 6379:6379 -d redis
    ```

    The client is meant to use a different instance, so we can test the server and client on the same machine. To start a new Redis container for the client, run the following command:

    ```bash
    docker run --name redis-client -p 6380:6379 -d redis
    ```
    The client will connect to the Redis server running on port 6380.


## License

[The MIT License](https://choosealicense.com/licenses/mit/)