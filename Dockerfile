# Use an official Python runtime as a parent image
#FROM python:3.6-slim

FROM python:3.7-alpine as base
FROM base as builder

# Let's multi-stage the build and avoid including the cached package installs
RUN mkdir /install
WORKDIR /install
# Let's utilise the caching of layers and put the requirements in early!
COPY requirements.txt /requirements.txt
RUN pip install --trusted-host pypi.python.org --install-option="--prefix=/install" -r /requirements.txt

# Then revert to Base and build the image
FROM base
COPY --from=builder /install /usr/local
# Future improvement: place the relevant app files in /src instead of the root?
COPY . /app
# Set the working directory to /app
WORKDIR /app

# Make port 80 available to the world outside this container
EXPOSE 80

# Define environment variable
ENV NAME JSON schema validation API

# Run app.py when the container launches
CMD ["python", "app.py"]