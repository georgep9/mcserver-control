
# Using Docker Compose with NGINX and Flask

Control panel for managing the startup and shutdown of Minecraft server. 

A Python web application that uses [boto3](https://boto3.amazonaws.com/v1/documentation/api/latest/index.html) to manage an EC2 instance and [paramiko](https://www.paramiko.org/) to run remote shell commands.

# Example

Here is the `docker-compose.yml` that powers the whole setup.

```yaml
version: "3.8"

services:
  nginx:
    container_name: nginx
    build:
      context: .
      target: nginx-server
    ports:
      - "80:80"
    depends_on:
      - backend
  backend:
    container_name: backend
    build:
      context: .
      target: flask-backend
    environment:
      EC2_ADDRESS: ${EC2_ADDRESS}
      EC2_ID: ${EC2_ID}
      EC2_USER: ${EC2_USER}
      LOGIN_PIN: ${LOGIN_PIN}
      SSH_KEY: ${SSH_KEY}
      SSH_KEY_DIR: ${SSH_KEY_DIR}
    volumes:
      - ~/.aws/:/root/.aws:ro
      - ~/.ssh/minecraft_server.pem:/root/.ssh/minecraft_server.pem:ro
    ports:
      - "5000:5000"
```

Here is the startup script the web application runs via SSH. It start a new tmux session running a Java Minecraft server.

```bash
SESSION_NAME="minecraft-server"

SERVER_DIR="$HOME/minecraft-server"
SERVER_JAR="server.jar"

INIT_MEM="-Xms1024M"
MAX_MEM="-Xmx1024m"

tmux has-session -t $SESSION_NAME 2>/dev/null
if [ $? -eq 0 ];
then
    echo "Minecraft server already running."
    exit 0
fi

cd $SERVER_DIR
tmux new-session -d -s $SESSION_NAME "java $MAX_MEM $INIT_MEM -jar $SERVER_JAR nogui"
```

# All in one

How to test this?

1. [Install Docker Compose](https://docs.docker.com/compose/install/)
1. Clone this repository
1. Update your `environment` values in `docker-compose.yml`
    - `EC2_ADDRESS`, `EC2_ID`, `EC2_USER` of your instance that will host the Minecraft server
    - `SSH_KEY`, `SSH_KEY_DIR` needed to establish SSH connection with instance
    - `LOGIN_PIN` passcode for the front-end client access
1. Run all containers with `docker-compose up -d`