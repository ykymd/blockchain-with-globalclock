docker run --network myblockchain_blockchain controller curl -sL -X POST \
    http://myblockchain_miner_1/nodes/register \
    -H 'Cache-Control: no-cache' \
    -H 'Content-Type: application/json' \
    -d '{
        "nodes": ["http://myblockchain_bc_1", "http://myblockchain_miner_2"]
    }'
docker run --network myblockchain_blockchain controller curl -sL -X POST \
    http://myblockchain_miner_2/nodes/register \
    -H 'Cache-Control: no-cache' \
    -H 'Content-Type: application/json' \
    -d '{
        "nodes": ["http://myblockchain_bc_2"]
    }'
