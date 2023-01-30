# murmur

This is going to be a kind of simulator to account for the dispersion and
vacillation of various inflected word forms in the Hungarian language.

This project is MIT Licensed.

## Note on Kivy installation

The murmur GUI is built with the Kivy framework, which is not shipped with
Python by default, so you will have to install it. These steps worked for
me on Debian 10.12:

sudo apt-get update  
\# Here's how to get the SDL2 backend working.  
\# Credits: https://stackoverflow.com/questions/60096291/how-can-i-get-kivy-to-use-sdl2-on-linux  
sudo apt-get install build-essential python-dev ffmpeg libsdl2-dev libsdl2-image-dev libsdl2-mixer-dev libsdl2-ttf-dev libportmidi-dev libswscale-dev libavformat-dev libavcodec-dev zlib1g-dev  
pip3 install --no-binary kivy kivy  
