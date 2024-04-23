# Discord Chat GPT Bot

The following sections describe how to setup the system so it will
run *locally* (i.e. on your laptop).  For deployment on an EC2 
instance, see the sections in the [Running with Docker in EC2 Instance](#running-with-docker-in-ec2-instance)

## Running Bot Locally

To run this application on your local device, follow the steps below:

Ensure you have the necessary dependencies installed. This will vary based on the programming language and libraries used in the project.

### Clone the repository to your local machine using the following command in your terminal:

```
git clone <repository_url>
```

>
### Navigate into the project directory:
>
 ```
cd <project_directory>
  ```

### Create .env file

Create a file `.env` that contains the hostname and port number for Redis.  We will run Redis on our laptop (`localhost`) using the standard Redis port (6379).  Replace `<Discord_Token>` with your Discord Token and `<OPENAI_KEY>` with your OPENAI key:

  ```
    DISCORD_TOKEN = '<Discord_Token>'
    OPENAI_KEY = "<OPENAI_KEY?"
    REDIS_HOST=localhost
    REDIS_PORT=6379
  ```

### Run the localdeploy.sh script:

Do 'bash localdeploy.sh'. This script should handle the setup, create a virtual environment, install dependencies, run redis as a background process, and start the bot application.


## Running with Docker in EC2 Instance

To run this application using Docker, follow the steps below:

### ssh into your EC2 instance

ssh -i ~/.ssh/labsuser.pem ec2-user@ip-address

### Use the scp command to copy your local files up to your EC2 instance

```
scp -i /path/to/your/key.pem /path/to/local/file.txt ec2-user@your-ec2-ip-address:/path/to/remote/directory
```

### Navigate into the project directory:
>
 ```
cd <project_directory>
  ```

#### Create .env file

Create a file `.env` that contains the hostname and port number for Redis.  We will run Redis on our laptop (`localhost`) using the standard Redis port (6379).  Replace `<Discord_Token>` with your Discord Token and `<OPENAI_KEY>` with your OPENAI key:

  ```
    DISCORD_TOKEN = '<Discord_Token>'
    OPENAI_KEY = "<OPENAI_KEY?"
    REDIS_HOST=localhost
    REDIS_PORT=6379
  ```

### Run the dockerdeploy.sh script:

Do 'bash dockerdeploy.sh'. This script should handle the setup, install docker on the EC2 instance, install dependencies, run redis as a background process, run docker as a system process and compose bot application