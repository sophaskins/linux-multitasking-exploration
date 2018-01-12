#! /bin/bash

./fake-process1 -duration 10 -freq 100 &
./fake-process2 -duration 20 -freq 100 &
./fake-process3 -duration 30 -freq 100 &
./fake-process4 -duration 40 -freq 100 &
./fake-process5 -duration 50 -freq 100 &
./fake-process6 -duration 60 -freq 100 &
python3 stats.py --output=datasets/six-different-cycles.csv --interval=10 &
