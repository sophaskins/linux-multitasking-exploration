#! /bin/bash

ps aux | grep stats.py | awk '{print $2}' | xargs kill
ps aux | grep fake | awk '{print $2}' | xargs kill
