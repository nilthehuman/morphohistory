# murmur

This is going to be a kind of simulator to account for the dispersion and
vacillation of various inflected word forms in the Hungarian language.

This project is MIT Licensed.

## Note on Kivy installation

The murmur GUI is built with the Kivy framework, which is not shipped with
Python by default, so you will have to install it. These steps worked for
me on Debian 10.12:

sudo apt-get update  
pip3 install ffpyplayer  
\# PyGame is a deprecated backend but I could not get the X11 backend working  
pip3 install pygame  
pip3 install kivy  
