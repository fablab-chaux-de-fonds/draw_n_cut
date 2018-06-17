#!/bin/bash

convert asdf.png -colorspace gray mono.png
convert mono.png -channel RGBA  -blur 0x2 monoblur.png
convert monoblur.png -colorspace gray +dither -posterize 12 mono12.png

convert mono12.png -unique-colors -scale 1000%  colors12.png
convert mono12.png -unique-colors txt:-

#convert mono12.png   -colors 2 +dither -colorspace gray -normalize  colors2.png
convert asdf.png  -separate -threshold 50% -combine     asdf.gif

convert mono12.png -threshold 10% thres_10.png
convert mono12.png -threshold 20% thres_20.png
convert mono12.png -threshold 30% thres_30.png
convert mono12.png -threshold 40% thres_40.png
convert mono12.png -threshold 50% thres_50.png
convert mono12.png -threshold 60% thres_60.png
convert mono12.png -threshold 70% thres_70.png
convert mono12.png -threshold 80% thres_80.png
convert mono12.png -threshold 90% thres_90.png
convert mono12.png mono12.ppm
potrace -b pdf -t 1000 -s mono12.ppm -o asdf.pdf


#OLD
#convert asdf.png -colorspace gray +dither -posterize 12 mono12.png
##potrace -t 1000 -a 1.5 -s mono12.ppm -o asdf.svg

