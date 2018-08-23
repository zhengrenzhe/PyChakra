#!/bin/bash

PLATFORM=`uname`

if [ $PLATFORM = "Darwin" ]; then
    FiLENAME="cc_osx_x64_1_10_2"
elif [ $PLATFORM = "Linux" ]; then
    FiLENAME="cc_linux_x64_1_10_2"
fi

if [ ! -f $FiLENAME ]; then
    wget `expr https://aka.ms/chakracore/"$FiLENAME"`
fi
tar -zxvf $FiLENAME
cp ChakraCoreFiles/lib/* PyChakra
