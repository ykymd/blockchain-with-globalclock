docker exec myblockchain_bc_1 mongod --fork --dbpath /var/lib/mongodb --logpath /var/log/mongodb.log
docker exec myblockchain_bc_2 mongod --fork --dbpath /var/lib/mongodb --logpath /var/log/mongodb.log
docker exec myblockchain_miner_1 mongod --fork --dbpath /var/lib/mongodb --logpath /var/log/mongodb.log
docker exec myblockchain_miner_2 mongod --fork --dbpath /var/lib/mongodb --logpath /var/log/mongodb.log