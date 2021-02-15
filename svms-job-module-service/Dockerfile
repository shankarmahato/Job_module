# Use the official Python image from the Docker Hub
FROM python:3.8-slim-buster

RUN apt-get update && apt-get install -y libmariadb-dev gcc openssh-server
RUN echo PermitRootLogin yes >> /etc/ssh/sshd_config
RUN echo root:newadminpasswd | chpasswd

# These two environment variables prevent __pycache__/ files.
ENV PYTHONUNBUFFERED 1
ENV PYTHONDONTWRITEBYTECODE 1

# Make a new directory to put our code in.
RUN mkdir /code/
RUN mkdir /code/logs

# Copy the requirements.txt file.
COPY ./requirements.txt /code/

# Change the working directory. 
# Every command after this will be run from the /code directory.
WORKDIR /code

# Copy the settings file
#COPY simplify_job/settings.yaml 

# Upgrade pip
RUN pip install --upgrade pip

#changing ulinits
RUN echo fs.file-max = 100000 >> /etc/sysctl.conf

# Install the requirements.
RUN pip install -r requirements.txt

# Copy the rest of the code. 
COPY . /code/ 
RUN chmod +x start.sh

ENTRYPOINT ["/code/start.sh"]

# Adding ports
EXPOSE 8002 22
