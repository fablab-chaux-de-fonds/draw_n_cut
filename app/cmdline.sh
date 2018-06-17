#!/bin/bash

potrace -t 100 -W 8in -H 6in  -u 10 --fillcolor  -s ./img/testTH.ppm -o ./vector/test.svg
inkscape --without-gui --file=./vector/test.svg --export-pdf=./vector/test.pdf --export-area-drawing
