#!/bin/bash

wget -r --no-parent --reject "index.html*" https://data.ciirc.cvut.cz/public/groups/incognite/myGym/yolact/yolact_weights_realworld.pth

mv -T data.ciirc.cvut.cz/public/groups/incognite/myGym/yolact/yolact_weights_realworld.pth ./yolact_weights_realworld.pth

rm -r data.ciirc.cvut.cz
