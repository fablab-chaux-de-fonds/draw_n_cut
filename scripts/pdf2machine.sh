#!/bin/bash

pstoedit -f plot-hpgl asdf.pdf hpgl/fulloutput.hpgl

./hpgl-distiller -i hpgl/fulloutput.hpgl -o hpgl/distilled.hpgl

cat hpgl/distilled.hpgl > txt/distilled.txt
cat hpgl/fulloutput.hpgl > txt/fulloutput.txt

#cat hpgl/distilled.hpgl > /dev/ttyUSB0
