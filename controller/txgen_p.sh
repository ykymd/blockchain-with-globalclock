#!/bin/sh
num=$1
a=1
while true ; do
docker run --network myblockchain_blockchain controller curl -sL -X POST \
  http://myblockchain_bc_$a/transaction/new \
  -H 'Content-Type: application/json' \
  -d '{"recipient": "053263f820054c2c8b3cec23c40a73a3", "amount": '$a' }' &
sleep $2
a=$(($a % $num + 1))
done
