#!/bin/bash -f

for i in 1 2 3 4 5 6 7 8
do
	echo "Testing GPIO $i"

	echo "Turning on"
	read -p "Press any key to continue... " -n1 -s
	echo out > /gpio/boardio$i/direction
	echo 1 > /gpio/boardio$i/value

	echo ""

	echo "Turning off"
	read -p "Press any key to continue... " -n1 -s
	echo 0 > /gpio/boardio$i/value

	echo ""

	echo "Reading Value"
	read -p "Press any key to continue... " -n1 -s
	echo ""
	echo in > /gpio/boardio$i/direction
	sleep 1
	cat /gpio/boardio$i/value

	echo ""
	read -p "Press any key to continue... " -n1 -s
	echo ""
done
