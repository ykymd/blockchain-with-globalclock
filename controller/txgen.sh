#!/bin/sh
while true ; do
docker run --network myblockchain_blockchain controller curl -sL -X POST \
  http://myblockchain_bc_1/transaction/new \
  -H 'Content-Type: application/json' \
  -d '{
    "recipient": "053263f820054c2c8b3cec23c40a73a3",
    "amount": 5
  }'
sleep 0.1
done