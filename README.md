# Introduction
A report generation service, that gets input data from RabbitMQ queue, requests aggregated data from mongodb database, and proceeds report to another RabbitMQ queue.

# Stack
Python, pika, pymongo, MongoDB, RabbitMQ

# The definition of service Calls-data-reporter:
- receives a task to generate a report via RabbitMQ (the task contains a list of 10 ids). 

Example of input message:
```
{
    "correlation_id": 13242421424214,
    "phones": [1,2,3,4,5,6,7,8,9,10]
}
```
- aggregates data by number (phone field) and returns a response to the client in the form of json. 

Example of output message:
```
  {
    "correlation_id": 13242421424214,
    "status": "Complete",
    "task_received": "2023-05-09 02:27:03.049772",
    "from": "report_service",
    "to": "client",
    "data": [
        {
            "phone": 2,
            "cnt_all_attempts": 12675,          # number of lines
            "cnt_att_dur": {                    # the number of lines in terms of duration (up to 10 seconds, from 10 to 30, from 30)
                "10_sec": 675,
                "10_30_sec": 2000,
                "30_sec": 12000
            },
            "min_price_att": 30,                # the price of the cheapest attempt (price = duration * 10)
            "max_price_att": 1500,              # the price of the most expensive attempt (price = duration * 10)
            "avg_dur_att": 46.7,                # medium duration
            "sum_price_att_over_15": 2765.59    # the sum of prices whose duration is more than 15 seconds
        },
        {
            "phone": 6,
            "cnt_all_attempts": 46759,
            "cnt_att_dur": {
                "10_sec": 759,
                "10_30_sec": 6000,
                "30_sec": 40000
            },
            "min_price_att": 27.86,
            "max_price_att": 2876.55,
            "avg_dur_att": 123.7,
            "sum_price_att_over_15": 4075.62
        }
    ],
    "total_duration": 3.67844633636             # total duration of execution
}

```
- A response contains the execution time of each report (total_duration)
- The service receives several such tasks from the client simultaneously and returns responses asynchronously
- Example of DB data.json has 2_000_000 records, but we assume that it can be much larger
- The service aggregates data on DB side
- The service is scalable horizontally

### Perfomance
- One instance of service processes one task for 3 seconds in average

### Configuration
Configuration parameteres have to be populated in .env, .env.<env_name> files.
Docker-compose uses file .env.

| Parameter name             | Description                                                    | Local run with existing infrastructure | Run with docker-compose        |
|----------------------------|----------------------------------------------------------------|----------------------------------------|--------------------------------|
| MONGO_INITDB_ROOT_USERNAME | MongoDB initial user name                                      | Not used                               | Use defaults from .env.example |
| MONGO_INITDB_ROOT_PASSWORD | MongoDB initial user password                                  | Not used                               |                                |
| MONGO_INITDB_DATABASE      | MongoDB initial db name                                        | Not used                               |                                |
| MONGODB_HOST               | MongoDB DB name                                                | Existing MongoDB host                  |                                |
| MONGODB_PORT               | MongoDB connection port                                        | Existing MongoDB port                  |                                |
| MONGODB_USER               | MongoDB user                                                   | Existing MongoDB user                  |                                |
| MONGODB_PASSWORD           | MongoDB user password                                          | Password of existing MongoDB user      |                                |
| MONGODB_DB_NAME            | MongoDB DB name                                                | Name of existing MongoDB database      |                                |
| RABBITMQ_HOST              | RabbitMQ host                                                  | Existing RabbitMQ host                 |                                |
| RABBITMQ_PORT              | RabbitMQ port                                                  | Existing RabbitMQ port                 |                                |
| RABBITMQ_USER              | RabbitMQ user                                                  | Existing RabbitMQ user                 |                                |
| RABBITMQ_PASSWORD          | RabbitMQ user password                                         | Password of existing RabbitMQ user     |                                |
| RABBITMQ_VIRTUAL_HOST      | RabbitMQ virtual host                                          | Existing RabbitMQ virtual host         |                                |
| RABBITMQ_QUEUE_NAME        | The queue name with input tasks. Will be created if not exists |                                        |                                |
| RABBITMQ_QUEUE_NAME_RESULT | The queue name for sending results. Will be created if not exists |                                        |                                |


# Run locally
1. Create mongoDB database and user, create collection 
2. Unpack data.js from ./docker/mongo-seed/data.zip, feed collection with data from data.json using mongoimport or other tool
3. Create index by field 'phone' in collection 
4. Create virtual host on RabbitMQ server
5. From .env.example create .env.local file with actual connection parameters to mongodb and rabbitmq
6. Use the tools/producer.py script to generate the required number of tasks with random keys (phone numbers): 
```
  python ./tools/producer.py .env.local
```
4. Run command
```
  python consumer.py .env.local
```
5. Connect to RabbitMQ to see queues which names are defined in config under RABBITMQ_QUEUE_NAME and RABBITMQ_QUEUE_NAME_RESULT variables

# Docker compose
## The infrastructure:
docker-compose.yml file describes all the infrastructure:

| Service name   | Description                                                             | Dependencies                                         | 
|----------------|-------------------------------------------------------------------------|------------------------------------------------------|
| rabbitmq       | RabbitMQ server                                                         | ---                                                  |
| mongo_db       | MongoDB server with permanent storage                                   | ---                                                  |
| mongo_seed     | Seeding mongo database with data from data.json                         | mongo_db: health-check                               |
| reporter_app   | Reporter application, built with Dockerfile. Can be scaled horizontally | mongo_db, rabbitmq: health-check; mongo-seed: exited |

## Run with docker-compose
1. Unpack data.js from ./docker/mongo-seed/data.zip into ./docker/mongo-seed/
2. From .env.example create .env file, change parameters if necessary. Do not change username and password for rabbitmq.
3. Run 
```
  docker-compose up
```
4. From .env.local.example create .env.local file, change parameters for rabbitmq if necessary. Bear in mind that RABBITMQ_PORT parameter in .env.local must match the port, mapped on localhost to container rabbitmq in docker.
5. Use the ./tools/producer.py script to generate the required number of tasks with random keys (phone numbers): 
```
  python ./tools/producer.py .env.local
```
Bear in mind that is takes up to 5 minutes for mongo_seed container to finish loading data to DB, reporter-app containers will run after mongo_seed exits

For stopping docker-compose containers, use following shell command:
```
  docker compose down -v --remove-orphans
```