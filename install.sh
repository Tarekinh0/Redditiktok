#! /bin/bash

sudo apt update
sudo apt install python-is-python3
sudo apt install python3 
sudo apt install python3-pip
sudo apt install xdg-utils
sudo apt install imagemagick, libmagick++-dev

sudo sed -i 's/rights="none"/rights="read | write"/' /etc/ImageMagick-6/policy.xml

# installing firefox (not from apt or snap because marionette problems otherwise)
sudo install -d -m 0755 /etc/apt/keyrings
wget -q https://packages.mozilla.org/apt/repo-signing-key.gpg -O- | sudo tee /etc/apt/keyrings/packages.mozilla.org.asc > /dev/null
echo "deb [signed-by=/etc/apt/keyrings/packages.mozilla.org.asc] https://packages.mozilla.org/apt mozilla main" | sudo tee -a /etc/apt/sources.list.d/mozilla.list > /dev/null
echo '
Package: *
Pin: origin packages.mozilla.org
Pin-Priority: 1000
' | sudo tee /etc/apt/preferences.d/mozilla
sudo apt update && sudo apt install firefox

pip install -r requirements.txt
mkdir generatedVideos
mkdir temp
mkdir templateGamePlayVideos
sudo chmod +x bot.py

cd templateGamePlayVideos
python ../other_scripts/youtubeDownload.py
cd ..

sudo echo "PATH/bot.py=PATH:$(pwd)" >> ~/.bashrc
sudo echo "./bot.py &" >> ./bashrc

echo "PLEASE DO NOT FORGET TO FILL IN default_config.json AND RENAMING IT TO config.json "

echo "ADD IT TO BOOT IF YOU RUN IT ON A SERVER :)\n Then launch it manually right now with './bot.py &' or restart your machine"
