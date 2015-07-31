# Makefile
#
# $Id$
#

SOURCE_R = serial_read_test.c
OBJ_R = serial_read_test

SOURCE_W = serial_write_test.c
OBJ_W = serial_write_test

INSTALL_PATH = /usr/local/bin


all: $(OBJ_R) $(OBJ_W)

$(OBJ_R): $(SOURCE_R)
	gcc -Wall -pedantic -o $(OBJ_R) $(SOURCE_R)
	
$(OBJ_W): $(SOURCE_W)
	gcc -Wall -pedantic -o $(OBJ_W) $(SOURCE_W)
	
install: all
	cp $(OBJ_R) $(INSTALL_PATH)/$(OBJ_R)
	cp $(OBJ_W) $(INSTALL_PATH)/$(OBJ_W)

clean:
	rm -f $(OBJ_R) $(OBJ_W)

