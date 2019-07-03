# JSON schema validation service
A basic Python API that serves as a JSON schema validation service

## Getting started
These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See deployment for notes on how to deploy the project on a live system.

### Prerequisites
You will need a local installation of Python and some of the modules
```
Fetch an installation for your operating system from https://www.python.org/downloads
```

### Installing
Install Python and make sure you have an up-to-date version of pip
```
pip install --upgrade pip
python -m pip install --upgrade pip (recommended for Windows)
```

And at least the module flask
```
pip install flask
```

To execute the application
```
python app.py
```

### Data files
The data files used are:
```
/data - example data of
/schema - imported by the API and used to validate the API calls
/templates - basic html templates
```


## Deployment
The deployment image is built with Docker
```
docker build --rm --tag=validator .
```

Run the Docker image locally and access it via http://localhost:4000
```
docker run -p 4000:80 validator
```

## Built with
* [Python](https://www.python.org/downloads/) - The application language
* [Flask](http://flask.pocoo.org/) - HTTP framework used
* [Docker](https://www.docker.com/) - Used to generate the images
* [Azure](https://azure.microsoft.com) - Used to run the Docker containers

## Contributing
Please use common sense and get in touch with me for any questions.

## Versioning
We use [SemVer](http://semver.org/) for versioning.

## Authors
* **Anders Demant van der Weide** - *Initial work* - [Antra](https://github.com/antra)

See also the list of [contributors](https://github.com/Antra/json-validate-api/contributors) who participated in this project.

## Licensing
This project is licensed under the GNU General Public License v3 - see the [LICENSE.md](LICENSE.md) file for details

## Acknowledgements
Thanks to everyone who provided comments and insights to get this started!
