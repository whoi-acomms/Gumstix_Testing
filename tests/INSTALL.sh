#!/bin/bash -f
TEST_DIR=/home/acomms/tests

#Create the test directory
mkdir -p $TEST_DIR
cp -af gumstix_*.sh $TEST_DIR/.

#Build the tests
(cd adc-test; make build; cp -af adc-test $TEST_DIR/.)
(cd watchdog-test; make build; cp -af watchdog-test $TEST_DIR/.)

#Copy the Audio Tests up a directory.
(cd audio\ tests; cp -af * $TEST_DIR/.)

