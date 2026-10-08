#!/bin/sh
# usage: dl.sh PAGE URL  -> saves shots/pNN.png
n=$(printf %02d "$1"); curl -sS -o "/home/user/cleanpro/catalogo-xpromise/raw/shots/p$n.png" "$2" && python3 -c "from PIL import Image;im=Image.open('/home/user/cleanpro/catalogo-xpromise/raw/shots/p$n.png');print('p$n',im.size)"
