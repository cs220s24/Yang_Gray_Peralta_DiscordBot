#!/bin/bash

# Check if .env file exists
if [ ! -f .env ]; then
    echo "Create .env before deploying"
    exit
fi

# Update the package lists for upgrades and new package installations
sudo yum update -y

# Install Docker
sudo yum install -y docker

# Enable Docker to start on boot
sudo systemctl enable docker

# Start the Docker service
sudo systemctl start docker

# Add the ec2-user to the docker group 
sudo usermod -a -G docker ec2-user

# Install Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Navigate to the directory containing your Docker Compose file
cd /home/ec2-user/app

# Build and start the Docker containers
sudo docker-compose up --build -d