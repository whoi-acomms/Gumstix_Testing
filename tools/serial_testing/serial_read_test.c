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
        
volatile int STOP=FALSE; 

FILE *open_output_file(char *outputfilename);
int get_baudrate_flag(char *baudrate_string);

       
int main(int argc, char *argv[])
{
	int fd, nread, nwritten;
	struct termios oldtio,newtio;
	char buf[256];
	FILE *outfp;
	int baudrate_flag;
	int nbytes_to_read, init_timeout_s, final_timeout_s, total_bytes_read;
	struct timeval start;
	struct timeval now;
	int time_elapsed, last_time_elapsed;

	if (argc != 7) {
		fprintf(stderr, "Usage: %s serialdevice baudrate nbytes init_timeout final_timeout outputfile\n", argv[0]);
		exit(-1);
	}

	baudrate_flag = get_baudrate_flag(argv[2]);
	outfp = open_output_file(argv[6]);
	nbytes_to_read = atoi(argv[3]);
	if (nbytes_to_read < 0) {
		fprintf(stderr, "nbytes=%d<0\n", nbytes_to_read);
		exit(-2);
	} 
	init_timeout_s = atoi(argv[4]);
	if (init_timeout_s < 0) {
		fprintf(stderr, "init_timeout=%d<0 seconds\n", init_timeout_s);
		exit(-3);
	} 
	final_timeout_s = atoi(argv[5]);
	if (final_timeout_s < 0) {
		fprintf(stderr, "final_timeout=%d<0 seconds\n", final_timeout_s);
		exit(-4);
	} 
	fd = open(argv[1], O_RDWR | O_NOCTTY ); 
	if (fd <0) {
		fprintf(stderr, "Could not open serial device\n");
		perror(argv[1]);
		exit(-5);
	}

	tcgetattr(fd,&oldtio); /* save current port settings */

	bzero(&newtio, sizeof(newtio));
	newtio.c_cflag = baudrate_flag | CRTSCTS | CS8 | CLOCAL | CREAD;
	newtio.c_iflag = IGNPAR;
	newtio.c_oflag = 0;
			
	/* set input mode (non-canonical, no echo,...) */
	newtio.c_lflag = 0;
	newtio.c_cc[VTIME]    = 10;   /* inter-character timer in deci-seconds */
	newtio.c_cc[VMIN]     = 0;   /* non-blocking read to allow timeout */
	tcflush(fd, TCIFLUSH);
	tcsetattr(fd,TCSANOW,&newtio);

	total_bytes_read = 0;
	last_time_elapsed = 0;
	(void) gettimeofday(&start, NULL);
	while (1) {       /* loop for input */
		nread = read(fd,buf,255);   /* non-blocking read */
		buf[nread]=0;               /* so we can printf... */
		if (nread>0) {
			total_bytes_read += nread;
			fprintf(stdout,"%s", buf);
			nwritten=fwrite(buf, 1, nread, outfp);
			fflush(outfp);
			if (nwritten != nread) {
				fprintf(stderr, "Tried to write %d bytes, only wrote %d bytes. Total read=%d\n", nread, nwritten, total_bytes_read);
				perror("writing output file");
				exit(-5);
			}
			(void) gettimeofday(&start, NULL);
		} else if (nread < 0) {
			fprintf(stderr, "read returned %d. Total read=%d\n", nread, total_bytes_read);
			perror("reading from device");
			break;
		}
		if (total_bytes_read >= nbytes_to_read) break;
		(void) gettimeofday(&now, NULL);
		time_elapsed = now.tv_sec - start.tv_sec;
		if (time_elapsed >= last_time_elapsed + 10) {
			fprintf(stderr, "time elapsed from last event = %d sec\n", time_elapsed);
			last_time_elapsed = time_elapsed;
		}
		if (0==total_bytes_read && time_elapsed > init_timeout_s) break;
		if (total_bytes_read>0 && time_elapsed > final_timeout_s) break;
	}
	fclose(outfp);
	tcsetattr(fd,TCSANOW,&oldtio);
	exit(0);
}


FILE *open_output_file(char *outputfilename)
{
	FILE *outfp;
	outfp = fopen(outputfilename, "wb");
	if (NULL==outfp) {
		fprintf(stderr, "Couldn't open output file %s\n", outputfilename);
		perror("opening output file");
		exit(-6);
	}
	return outfp;
}

int get_baudrate_flag(char *baudrate_string)
{
	int baudrate;

	if (NULL==baudrate_string) {
		fprintf(stderr, "Empty baudrate string\n");
		exit(-7);
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
			exit(-8);
	}
}
