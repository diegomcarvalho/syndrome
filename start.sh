#!/bin/bash
cd /home/carvalho/cluster/syndrome
ray start --head --include-webui true --redis-port 6379 --redis-password dc
parallel-ssh -h machines -P -I < start_worker.sh
