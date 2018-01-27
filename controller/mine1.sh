#!/bin/sh
324287

# 初回マイニング
docker run --network myblockchain_blockchain controller curl -sL http://myblockchain_bc_1/mine?seed=324287

while true ; do
docker run --network myblockchain_blockchain controller curl -sL http://myblockchain_bc_1/mine
done