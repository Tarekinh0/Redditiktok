#! /bin/bash

pip install -r requirements.txt
mkdir generatedVideos
mkdir temp
mkdir templateGamePlayVideos
sudo chmod +x bot.py

cd templateGamePlayVideo
python ../Other\ scripts/youtubeDownload.py
cd ..

sudo echo "PATH/bot.py=PATH:$(pwd)" >> ~/.bashrc
sudo echo "./bot.py &" >> ./bashrc

echo "PLEASE DO NOT FORGET TO FILL IN default_config.json AND RENAMING IT TO config.json "

echo "ADD IT TO BOOT IF YOU RUN IT ON A SERVER :)\n Then launch it manually right now with './bot.py &' or restart your machine"