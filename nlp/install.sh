#!/bin/bash

# Install TweebankNLP from MIT-CCC
git clone https://github.com/mit-ccc/TweebankNLP.git
cd TweebankNLP
pip install -e ./twitter-stanza
pip install pythainlp==4.0.2

# Download pre-trained models for TweebankNLP
sh download_twitter_resources.sh

# Install other Python dependencies
pip install opensearch-py==2.2.0 click==8.1.5 casanova==1.15.1

# Downgrade protobuf to be compatible with dependency in stanza/protobuf/CoreNLP_pb2.py
pip install protobuf==3.19.0
