#!/bin/bash


# Download Cifar-10 dataset
mkdir ../app/data
cd ../app/data || exit
wget https://www.cs.toronto.edu/~kriz/cifar-10-python.tar.gz
tar -xvzf ./cifar-10-python.tar.gz
rm cifar-10-python.tar.gz

cd ../../scripts || exit

python3.9 -m venv ../venv

source ../venv/bin/activate

pip3 install -r ../requirements.txt
