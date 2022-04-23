#!/bin/bash

# sudo apt install inotify-tools

export RPI=plantpi.local

while inotifywait -r ./*; do
    rsync -ravz ../app pi@$RPI:~/ 
done
