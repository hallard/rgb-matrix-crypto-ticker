#!/bin/bash
# Download Crypto icons from coinmarketcap
# You need to get coinmarketcap crypto ID and coingecko according name 
# Search crypto name, example helium on coinmarketcap.com
# right click on crypto icon, select open image in a new tab
# then take url on the new tab, in my case it's 
# https://s2.coinmarketcap.com/static/img/coins/64x64/5665.png
# coinmarketcap Crypto id for Helium is at the end, in our case it's 5665
# so to save icon file launch this script with
#
# ./get_icons.sh 5665 helium
#
# helium is the crypto name from coingecko need to be the same to match
# copy then image into images/icons/ folder of this project 
# you will get 2 version of icon at the end
# helium_16.png for 16x16
# helium_32.png for 32x32
# copy files into images/currency folder
# since image may have some glitch on final RGB Matrix when used, I needed to adjust with GIMP (or other)
# the one I'm using for a better display (for now BitCoin, Helium, IoTex and Crypto.com). 

echo "Getting icon for coinmarketcap ID:$1 saving as $2_32.png"
# 16x16 will be used for 64x32 or 64x64 displays
curl -o $2_16.jpg  https://s2.coinmarketcap.com/static/img/coins/16x16/$1.png
# 32x32 will be used for 128x64 displays
curl -o $2_32.jpg  https://s2.coinmarketcap.com/static/img/coins/32x32/$1.png

#curl -o $2_64.jpg  https://s2.coinmarketcap.com/static/img/coins/64x64/$1.png
#curl -o $2_128.jpg  https://s2.coinmarketcap.com/static/img/coins/128x128/$1.png
#curl -o $2_200.jpg  https://s2.coinmarketcap.com/static/img/coins/200x200/$1.png
