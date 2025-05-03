#!/bin/bash

SERVER_FILES_DIR="./server_files"
CLIENT_FILES_DIR="./client_downloaded_files"

echo """########## Test cases ###########
Test 1:
    - Download a small file
    - Check if the downloaded file is the same as the original
Test 2:
    - Download a large file (~10 KB)
    - Check if the downloaded file is the same as the original
#################################"""


if [ "$EUID" -ne 0 ]; then
    echo "Please run as root"
    exit 1
fi

if [ ! -d "$SERVER_FILES_DIR" ]; then
    mkdir -p "$SERVER_FILES_DIR"
fi
if [ ! -d "$CLIENT_FILES_DIR" ]; then
    mkdir -p "$CLIENT_FILES_DIR"
else
    rm -rf "$CLIENT_FILES_DIR"/*
fi


check_test_passed() {
    local test_number=$1
    local test_file_name=$2
    local test_is_passed=1
    local reason=""

    check_file_is_downloaded "$test_file_name"
    if [ $? -eq 0 ]; then
        compare_files "$test_file_name"
        if [ $? -eq 0 ]; then
            test_is_passed=0
        else
            reason="Downloaded file is not the same as the original"
        fi
    else
        reason="File not downloaded"
    fi

    test $test_is_passed -eq 0 && echo "Test $test_number passed" || echo "Test $test_number failed: $reason"
}


check_file_is_downloaded() {
    local file_name=$1
    local file_path="$CLIENT_FILES_DIR/$file_name"

    test -f "$file_path" && return 0 || return 1
}

compare_files() {
    local file_name=$1
    local file_path="$CLIENT_FILES_DIR/$file_name"

    cmp -s "$file_path" "$SERVER_FILES_DIR/$file_name" && return 0 || return 1

}

test_file_name="test_1.txt"
echo "Test 1" > $SERVER_FILES_DIR/$test_file_name
python3 client.py > ./test_1_client.log 2>&1 <<EOF
$test_file_name
EOF

check_test_passed 1 $test_file_name

test_file_name="test_2.txt"
dd if=/dev/zero of=$SERVER_FILES_DIR/$test_file_name bs=10K count=1 > /dev/null 2>&1

python3 client.py > ./test_2_client.log 2>&1 <<EOF
$test_file_name
EOF

check_test_passed 2 $test_file_name



