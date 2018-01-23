#!/bin/sh
while true ; do
docker run --network myblockchain_blockchain controller curl -sL http://myblockchain_miner_1/mine
sleep 30
docker run --network myblockchain_blockchain controller curl -sL http://myblockchain_miner_2/mine
sleep 30
done