#!/bin/sh
#for i in `seq $1`
#do
#    id=$(($i+1))
#    docker run --network myblockchain_blockchain controller python linker.py "myblockchain_bc_$id" "myblockchain_bc_$i"
#done
for i in `seq $1`
do
    echo $i
    add=$(($RANDOM % ($1-1) + 1))
    echo $add
    id=$((($add+$i-1) % $1+1))
    echo $id
    docker run --network myblockchain_blockchain controller python linker.py "myblockchain_bc_$id" "myblockchain_bc_$i"
done
