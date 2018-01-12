#! /bin/bash

./fake-process2 &
./fake-process3 &
./fake-process4 &
./fake-process5 &
chrt --idle 0 ./fake-process6 &
python3 stats.py --output=datasets/four-normal-one-idle.csv --interval=10 &
