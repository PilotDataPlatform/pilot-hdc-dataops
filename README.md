# Dataops Service

[![Python](https://img.shields.io/badge/python-3.9-brightgreen.svg)](https://www.python.org/)

Responsible for:
- Writing file status updates to Redis for upload, download, copy, and delete jobs.
- Managing copy and delete operations for files and folders. This is accomplished by dispatching operation requests received by Portal to the Queue service.
- Generation and retrieval of previews for zipped files.


## Getting Started

To get a local copy of the service up and running follow these simple example steps.


### Prerequisites

This project is using [Poetry](https://python-poetry.org/docs/#installation) to handle the dependencies.

    curl -sSL https://install.python-poetry.org | python3 -

### Installation & Quick Start

1. Clone the project.

       git clone https://github.com/PilotDataPlatform/dataops.git

2. Install dependencies.

       poetry install

3. Run setup script for creating PostgreSQL database (schema is created during Alembic migration).

    - [Create database](https://github.com/PilotDataPlatform/dataops/blob/develop/migrations/scripts/create_db.sql)

5. Add environment variables into `.env` in case it's needed. Use `.env.schema` as a reference.


6. Run any initial scripts, migrations or database seeders.

       poetry run alembic upgrade head

7. Run application.

       poetry run python start.py

### Startup using Docker

This project can also be started using [Docker](https://www.docker.com/get-started/).

1. To build and start the service within the Docker container, run:

       docker compose up

2. Migrations should run automatically after the previous step. They can also be manually triggered:

       docker compose run --rm alembic upgrade head

## Contribution

You can contribute the project in following ways:

* Report a bug.
* Suggest a feature.
* Open a pull request for fixing issues or adding functionality. Please consider
  using [pre-commit](https://pre-commit.com) in this case.
* For general guidelines on how to contribute to the project, please take a look at the [contribution guides](CONTRIBUTING.md).

## Acknowledgements
The development of the HealthDataCloud open source software was supported by the EBRAINS research infrastructure, funded from the European Union's Horizon 2020 Framework Programme for Research and Innovation under the Specific Grant Agreement No. 945539 (Human Brain Project SGA3) and H2020 Research and Innovation Action Grant Interactive Computing E-Infrastructure for the Human Brain Project ICEI 800858.
