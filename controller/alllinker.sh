#!/bin/sh
for i in `seq $1`
do
    docker run --network myblockchain_blockchain controller curl -sL -X POST http://myblockchain_bc_$i/nodes/register/all -H 'Content-Type: application/json' -d '{"num": '$1'}'
done
