#!/bin/bash

cat ./test.txt > /dev/ttyUSB0
#cat ./testGPGL.txt > /dev/ttyUSB0


#exec 99<>/dev/ttyUSB0 
#printf "OA;\r" >&99
#read answer <&99 
#read answer <&99 
#exec 99<>&-
