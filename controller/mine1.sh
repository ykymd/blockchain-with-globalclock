#!/bin/sh

# 初回マイニング
docker run --network myblockchain_blockchain controller curl -sL http://myblockchain_bc_1/mine?seed=888273

while true ; do
docker run --network myblockchain_blockchain controller curl -sL http://myblockchain_bc_1/mine
done