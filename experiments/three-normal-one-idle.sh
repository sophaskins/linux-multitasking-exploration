#! /bin/bash

./fake-process2 &
./fake-process3 &
./fake-process4 &
chrt --idle 0 ./fake-process5 &
python3 stats.py --output=datasets/three-normal-one-idle.csv --interval=10
