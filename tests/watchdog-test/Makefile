#Makefile

SOURCE = watchdog-test.c
OBJ = watchdog-test
INSTALL_PATH = /usr/bin

build:
	gcc -o $(OBJ) $(SOURCE)
	
install: build
	cp $(OBJ) $(INSTALL_PATH)/$(OBJ)