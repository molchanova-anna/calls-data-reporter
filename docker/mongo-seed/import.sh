#! /bin/bash
# import data to collection from data.json
mongoimport --host $MONGODB_HOST --port $MONGODB_PORT -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin --db $MONGODB_DB_NAME --collection calls --drop --type json --file /mongo-seed/data.json --jsonArray;
# creating index on field "phone"
mongosh --host $MONGODB_HOST --port $MONGODB_PORT -u $MONGO_INITDB_ROOT_USERNAME -p $MONGO_INITDB_ROOT_PASSWORD --authenticationDatabase admin <<EOF
use $MONGODB_DB_NAME;
db.calls.createIndex({'phone': 1});
EOF