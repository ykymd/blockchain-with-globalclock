#!/bin/sh

while true ; do
docker run --network myblockchain_blockchain controller curl -sL http://myblockchain_bc_2/mine
done