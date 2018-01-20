#!/bin/sh
while true ; do
docker run --network myblockchain_blockchain controller curl -sL http://myblockchain_miner_1/mine
docker run --network myblockchain_blockchain controller curl -sL http://myblockchain_miner_2/mine
sleep 3
done