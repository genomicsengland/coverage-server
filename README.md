# Requirements

## Python Packages Requirements

All standard python packages required are specified in
the `requirements.txt` file

## System requirements

- **RabbitMQ server**
```
$ sudo apt-get install rabbitmq-server
```
- **Celery worker**. In production it should be a daemon working in the
background. For testing you can use:
```
# Run this in the root folder of the project
celery worker -A coveragedb -l info
```

- **MongoDB**. Follow https://docs.mongodb.com/manual/tutorial/install-mongodb-on-ubuntu/

# Prepare dev environment and running the app

### Migration
```
python manage.py migrate
```

### Add superuser
```
python manage.py createsuperuser
```

### Prepare MongoDB
```
python setup/start_coverage_db.py
```

### Run server daemon
```
python manage.py runserver
```

`Note:` By default it will create and use Sqlite DB.


# How to Use it

For most of the action you will use the API endpoints:
[Docs](http://127.0.0.1:8000/api/docs/)


## Create Gene Collection

Gene collections can only be created from the Admin panel. This tags
identify sets of genes that should be consider together.
[Admin gene collection](http://127.0.0.1:8000/admin/coveragedbingestion/genecollection/)

## Ingest Coverage Data

You will ingest coverage data for ONE sample and ONE gene collection,
these 2 fields, form a unique id, so you can not ingest the new data for
the same sample and same gene collection more than once before to delete
the first one.

You will simply use the endpoint: `/api/sample-ingestion/` with the
json request:

```
{
    "name": "sample_name",
    "input_file": "file_location",
    "gene_collection": "gene_collection_name"
}
```


This will send a job to the running worker, if there isn't any up or
available it will wait until an slot is available.

## Check Ingestion Status

You can always check the status of one ingestion job with the endpoint:
`/api/sample-ingestion/{name_and_gene_collection}/` (method GET)where
`name_and_gene_collection` will the the name of the sample and the name
of the gene collection separated by `-`

## Delete Coverage Data

You delete the inserted data with the endpoint:
`/api/sample-ingestion/{name_and_gene_collection}/` (method DELETE)
where `name_and_gene_collection` will the the name of the sample
 and the name of the gene collection separated by `-`

