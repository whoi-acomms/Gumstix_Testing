/* Copied from: http://tldp.org/HOWTO/Serial-Programming-HOWTO/x115.html
 * and hacked on from there.
 */
 

#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>
#include <termios.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/time.h>

#define _POSIX_SOURCE 1 /* POSIX compliant source */
#define FALSE 0
#define TRUE 1
        
FILE *open_input_file(char *inputfilename);
int get_baudrate_flag(char *baudrate_string);

       
int main(int argc, char *argv[])
{
	int fd, nread, nwritten;
	struct termios oldtio,newtio;
	char buf[256];
	FILE *infp;
	int baudrate_flag, total_bytes_read;

	if (argc != 4) {
		fprintf(stderr, "Usage: %s serialdevice baudrate inputfile\n", argv[0]);
		exit(-1);
	}

	baudrate_flag = get_baudrate_flag(argv[2]);
	infp = open_input_file(argv[3]);

	fd = open(argv[1], O_RDWR | O_NOCTTY ); 
	if (fd <0) {
		fprintf(stderr, "Could not open serial device\n");
		perror(argv[1]);
		exit(-2);
	}

	tcgetattr(fd,&oldtio); /* save current port settings */

	bzero(&newtio, sizeof(newtio));
	newtio.c_cflag = baudrate_flag | CRTSCTS | CS8 | CLOCAL | CREAD;
	newtio.c_iflag = IGNPAR;
	newtio.c_oflag = 0;
			
	/* set input mode (non-canonical, no echo,...) */
	newtio.c_lflag = 0;
	newtio.c_cc[VTIME]    = 0;   /* inter-character timer in deci-seconds */
	newtio.c_cc[VMIN]     = 1;   /* need to read at least one char on reads */
	tcflush(fd, TCIFLUSH);
	tcsetattr(fd,TCSANOW,&newtio);

	total_bytes_read = 0;
	while (!feof(infp) && !ferror(infp)) {       /* loop for input */
		nread = fread(buf,1,255,infp);
		if (nread>0) {
			total_bytes_read += nread;
			buf[nread]=0; /* so we can fprintf */
			fprintf(stdout,"%s", buf);
			nwritten=write(fd, buf, nread);
			/* tcflush(fd, TCIFLUSH); maybe not? */
			if (nwritten != nread) {
				fprintf(stderr, "Tried to write %d bytes, only wrote %d bytes. Total read=%d\n", nread, nwritten, total_bytes_read);
				perror("writing to device");
				exit(-5);
			}
		} else if (nread <= 0) {
			fprintf(stderr, "read returned %d. Total read=%d\n", nread, total_bytes_read);
			perror("reading from input file");
			break;
		}
	}
	fclose(infp);
	fprintf(stderr, "here, line=%d\n", __LINE__);
	tcflush(fd, TCIFLUSH);
	fprintf(stderr, "here, line=%d\n", __LINE__);
	tcsetattr(fd,TCSANOW,&oldtio);
	fprintf(stderr, "here, line=%d\n", __LINE__);
	close(fd);
	fprintf(stderr, "here, line=%d\n", __LINE__);
	exit(0);
}


FILE *open_input_file(char *inputfilename)
{
	FILE *infp;
	infp = fopen(inputfilename, "rb");
	if (NULL==infp) {
		fprintf(stderr, "Couldn't open input file %s\n", inputfilename);
		perror("opening input file");
		exit(-3);
	}
	return infp;
}

int get_baudrate_flag(char *baudrate_string)
{
	int baudrate;

	if (NULL==baudrate_string) {
		fprintf(stderr, "Empty baudrate string\n");
		exit(-4);
	}

	baudrate = atoi(baudrate_string);

	switch (baudrate) {
		case 2400: return B2400;
		case 4800: return B4800;
		case 9600: return B19200;
		case 19200: return B19200;
		case 38400: return B38400;
		case 57600: return B57600;
		case 115200: return B115200;
		case 230400: return B230400;
		case 460800: return B460800;
		default:
			fprintf(stderr, "Unknown baudrate %s =? %d\n", baudrate_string, baudrate);
			exit(-5);
	}
}
