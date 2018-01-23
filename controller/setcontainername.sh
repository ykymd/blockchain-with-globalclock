#!/bin/sh
for i in `seq $1`
do
    docker exec myblockchain_bc_$i /bin/bash -c "export CONTAINER_NAME='http://myblockchain_bc_$i'"
done