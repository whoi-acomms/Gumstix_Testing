#Makefile

SOURCE = adc-test.c
OBJ = adc-test
INSTALL_PATH = /usr/bin

build:
	gcc -o $(OBJ) $(SOURCE)
	
install: build
	cp $(OBJ) $(INSTALL_PATH)/$(OBJ)