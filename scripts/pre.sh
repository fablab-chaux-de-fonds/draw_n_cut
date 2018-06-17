#!/bin/bash

convert asdf.png -colorspace gray mono.png
convert mono.png -channel RGBA  -blur 0x2 monoblur.png
convert monoblur.png -colorspace gray -posterize 12 mono12.png
#convert mono12.png mono12.ppm
#potrace -t 1000 -s mono12.ppm -o asdf.svg

#OLD
#convert asdf.png -colorspace gray +dither -posterize 12 mono12.png
##potrace -t 1000 -a 1.5 -s mono12.ppm -o asdf.svg

