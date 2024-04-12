# python-file-upload

## Installation

```bash
pip install -r requirements.txt
```

## Create DB

```bash
    docker pull postgres
    docker run --name db-postgres -e POSTGRES_DB=fileupload -e POSTGRES_USER=admin -e POSTGRES_PASSWORD=password -p 5432:5432 -d postgres
```

## Run the project

```bash
uvicorn main:app
```

```bash
python3 gui.py
```

## Documentation for the project.

To view Postman collection, click [here](https://documenter.getpostman.com/view/13139793/2sA3Bhea5Y)