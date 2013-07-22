#Makefile

SOURCE = devmem2.c
OBJ = devmem2
INSTALL_PATH = /sbin

build:
	gcc -o $(OBJ) $(SOURCE)
	
install: build
	cp $(OBJ) $(INSTALL_PATH)/$(OBJ)