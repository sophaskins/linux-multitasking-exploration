#! /bin/bash

./fake-process2 &
./fake-process3 &
./fake-process4 &
./fake-process5 &
python3 stats.py --output=datasets/four-normal.csv --interval=10 &
