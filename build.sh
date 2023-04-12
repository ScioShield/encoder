#!/bin/bash
# This is the build file for packaging either encoder.py or decoder.py to a Windows .exe
# You can run it yourself however there are dependencies such as vagrant that I won't cover

# Check if two arguments are given
if [[ $# -ne 2 ]]; then
   echo "Usage: $0 <encoder.py/decoder.py> <version>"
   exit 1
fi

# Set the arguments
APP="$1"
VERSION="$2"
DIST="./dist/${APP%.py}$VERSION.exe"


# Check if the app already exists and exit
if [[ -f "./dist/${APP%.py}$VERSION.exe" ]]; then
    echo "Error: ./dist/${APP%.py}$VERSION.exe already exists"
    exit 1
fi

# Run unit tests
if [[ "$APP" == "encoder.py" ]]; then
    python3 encoder_test.py
    if [[ "$?" -ne 0 ]]; then
        echo "Error: Unit tests for encoder.py failed"
        exit 1
    fi
else
    python3 decoder_test.py
    if [[ "$?" -ne 0 ]]; then
        echo "Error: Unit tests for decoder.py failed"
        exit 1
    fi
fi

# Check if machine is running and start if not
if ! vagrant status | grep running > /dev/null; then
    vagrant up
fi

# Build the app with appropriate version
if [[ "$APP" == "encoder.py" ]]; then
    vagrant winrm -e -s powershell -c "Invoke-Command -ScriptBlock { cd C:\vagrant\ ; pyinstaller --onefile --name encoder$VERSION.exe encoder.py }"
else
    vagrant winrm -e -s powershell -c "Invoke-Command -ScriptBlock { cd C:\vagrant\ ; pip install python-magic-bin ; pyinstaller --onefile --name decoder$VERSION decoder.py }"
fi

# Check if the app works as expected so it prints the help message
if ! vagrant winrm -e -c "Invoke-Command -ScriptBlock { cd C:\vagrant\ ; ./dist/${APP%.py}$VERSION.exe }" 2>&1 | grep 'usage'; then
    echo "Error: $APP executable file does not work as expected"
    exit 1
fi

echo "Build is successful"
exit 0
