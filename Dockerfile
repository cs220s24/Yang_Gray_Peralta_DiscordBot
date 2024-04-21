FROM amazonlinux

WORKDIR /app

# Install Python and pip
RUN yum -y update && yum -y install python3 python3-pip

COPY requirements.txt .

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copies all files from local directory into Docker image at the /app directory
COPY . .

# Run bot.py when the container launches
CMD python3 bot.py