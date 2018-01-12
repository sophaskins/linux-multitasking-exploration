#! /bin/bash

./fake-process2 &
./fake-process3 &
./fake-process4 &
./fake-process5 &
./fake-process6 &
python3 stats.py --output=datasets/five-normal.csv --interval=10 &
