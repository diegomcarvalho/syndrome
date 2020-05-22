#!/bin/bash
cd /home/carvalho/cluster/syndrome
parallel-ssh -h machines -P -I < stop_worker.sh
ray stop
