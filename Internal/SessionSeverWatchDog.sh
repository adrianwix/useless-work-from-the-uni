#!/bin/bash

while true ; do
	python3 GameSessionServer.py --all-interfaces
done
echo "$(date) : Watchdog finish" >> GameSessionServer.log

exit 0

