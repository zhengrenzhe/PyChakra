PLATFORM=`uname`

if [ $PLATFORM = "Darwin" ]; then
    FiLENAME="cc_osx_x64_1_8_2"
elif [ $PLATFORM = "Linux" ]; then
    FiLENAME="cc_linux_x64_1_8_2"
fi

# wget `expr https://aka.ms/chakracore/"$FiLENAME"`
tar -zxvf $FiLENAME
cp ChakraCoreFiles/lib/* PyChakra
