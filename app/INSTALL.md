
# Purpose

The software uses webcam to vectorize image data (for instance drawings) and then print them on a HPGL cutting machine.

# Software used

The software heavily uses command line software available in the linux distributions.

* imagemagick for some image conversions
* streamer for webcam capture 
* potrace to vectorize pixel images
* inkscape for some image conversions
* pstoedit to transform pdf files to hpgl

Please intall using the following command line

    sudo apt-get install imagemagick streamer potrace inkscape pstoedit


Two additional software is not available on distributions

* hpgl-distiller http://pldaniels.com/hpgl-distiller/ (need to be compiled)
* python anaconda with additional packages PyQT5, skimage for interface and image processing. Please install following the instructions here https://conda.io/docs/install/quick.html#linux-miniconda-install. We recommend to create a specific python environment as described here https://conda.io/docs/using/envs.html


# Additional settings

The software requires the user to have access to serial ports in writing. This is done by adding the user to the dialout group.


    sudo usermod -a -G dialout userName


