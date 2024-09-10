# Use Python image
FROM ubuntu:latest

# Set the working directory
WORKDIR /app

# Copy Python script into the container
COPY . /app

# Update apt packages
RUN apt update
RUN apt upgrade -y

# Install vim
RUN apt install vim -y

# Install python3
RUN apt install software-properties-common -y
RUN apt install python3 -y
RUN apt install python3-venv -y
RUN apt install libpq-dev python3-dev -y

# Install pip
RUN apt install python3-pip -y

# Install python libraries
RUN ["/bin/bash", "-c", "python3 -m venv sqlAlchemy; source sqlAlchemy/bin/activate; pip3 install -r requirements.txt;"] -y