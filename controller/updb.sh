#!/bin/sh
for i in `seq $1`
do
    docker exec myblockchain_bc_$i mongod --fork --dbpath /var/lib/mongodb --logpath /var/log/mongodb.log
done