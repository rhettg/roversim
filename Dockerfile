FROM python:3.10

# Install dependencies 
RUN pip install --upgrade pip


# Install any needed packages specified in requirements.txt
ADD requirements.txt /app/requirements.txt
RUN pip install -r /app/requirements.txt

WORKDIR /app

# Make port 8080 available to the world outside this container

EXPOSE 8080

# Run main.py
CMD ["python", "main.py"]