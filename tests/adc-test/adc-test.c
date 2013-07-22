/*
Copyright (C) 2012, Pansenti, LLC

Permission is hereby granted, free of charge, to any person obtaining a copy of
this software and associated documentation files (the "Software"), to deal in
the Software without restriction, including without limitation the rights to
use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies
of the Software, and to permit persons to whom the Software is furnished to do
so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
DEALINGS IN THE SOFTWARE.
*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <signal.h>
#include <sys/ioctl.h>
#include <time.h>
#include <sys/time.h>
#include <getopt.h>
#include <errno.h>

// the valid range is 0 - 2500, so this will work for an error
#define ADC_READ_ERROR -100000

#define ADC2 0
#define ADC3 1
#define ADC4 2
#define ADC5 3
#define ADC6 4
#define ADC7 5
#define NUM_ADC 6


char hwmonsyspath[] = "/sys/class/hwmon/hwmon0/device/";

void register_sig_handler();
void sigint_handler(int sig);
void msleep(int ms);
void show_elapsed(struct timeval *start, struct timeval *end, int count);
int loop(int delay_ms, int *list);
int open_adc(int adc);
int read_adc(int fd);

int abort_read;

void usage(char *argv_0)
{
    printf("\nUsage: %s <options> [adc-list]\n", argv_0);
    printf(" -d<delay-ms> Delay between reads, default 50, min 1\n");
    printf(" adc-list Space separated list of ADCs to monitor, 2-7\n");
    printf("\nExample:\n\t%s -d100 2 3 5\n", argv_0);

    exit(0);
}

int main(int argc, char **argv)
{
    int opt, delay_ms, adc, i;
    struct timeval start, end;
    int adc_list[NUM_ADC];

    register_sig_handler();

    delay_ms = 50;

    while ((opt = getopt(argc, argv, "d:h")) != -1) {
        switch (opt) {
        case 'd':
            delay_ms = atoi(optarg);

            if (delay_ms < 1) {
                printf("Invalid delay %d. Must be greater then zero.\n", delay_ms);
                usage(argv[0]);
            }

break;

        case 'h':
        default:
            usage(argv[0]);
            break;
        }
    }

    // now get the adc list
    if (optind == argc) {
        printf("A list of ADCs is required\n");
        usage(argv[0]);
    }

    memset(adc_list, 0, sizeof(adc_list));

    for (i = optind; i < argc; i++) {
        adc = atoi(argv[i]);

        if (adc < 2 || adc > 7) {
            printf("adc %d is out of range\n", adc);
            usage(argv[0]);
        }

        adc -= 2;
           
        if (adc_list[adc]) {
            printf("adc %d listed more then once\n", adc + 2);
            usage(argv[0]);
        }

        adc_list[adc] = 1;
    }

    if (gettimeofday(&start, NULL) < 0) {
        perror("gettimeofday: start");
        return 1;
    }

    int count = loop(delay_ms, adc_list);

    if (gettimeofday(&end, NULL) < 0)
        perror("gettimeofday: end");
    else
        show_elapsed(&start, &end, count);
        
    return 0;
}

// We know the diff is never going to be that big
void show_elapsed(struct timeval *start, struct timeval *end, int count)
{
    double diff;
    double rate;

    if (end->tv_usec > start->tv_usec) {
        diff = (double) (end->tv_usec - start->tv_usec);
    }
    else {
        diff = (double) ((1000000 + end->tv_usec) - start->tv_usec);
        end->tv_sec--;
    }

    diff /= 1000000.0;

    diff += (double)(end->tv_sec - start->tv_sec);

    if (diff > 0.0)
        rate = count / diff;
    else
        rate = 0.0;

    printf("Summary\n Elapsed: %0.2lf seconds\n Reads: %d\n Rate: %0.2lf Hz\n\n",
        diff, count, rate);
}

int loop(int delay_ms, int *list)
{
    int fd, count, i, update;
    int val[NUM_ADC];

    count = 0;
    memset(val, 0, sizeof(val));

    fprintf(stdout, "\n(use ctrl-c to stop)\n\n");

    fprintf(stdout, "ADC ");

    for (i = 0; i < NUM_ADC; i++) {
        if (list[i])
            fprintf(stdout, " %d", i + 2);
    }

    fprintf(stdout, "\n");

    while (!abort_read) {
        for (i = 0; i < NUM_ADC; i++) {
            if (!list[i])
                continue;
 
            // index zero is ADC 2
            fd = open_adc(i + 2);
            if (fd < 0)
                break;;

            val[i] = read_adc(fd);

            close(fd);

            if (val[i] == ADC_READ_ERROR)
                break;
        }

        update = 0;

        // don't spend too much time updating display
        if (delay_ms < 10) {
            // every 32nd read
            if ((count & 0x1f) == 0)
                update = 1;
        }
        else if (delay_ms < 50) {
            // every 8th read
            if ((count & 0x07) == 0)
                update = 1;
        }
        else {
            update = 1;
        }

        if (update) {
            fprintf(stdout, "\rRead %8d: ", count);

            for (i = 0; i < NUM_ADC; i++) {
                if (list[i])
                    fprintf(stdout, " %4d ", val[i]);
            }
            
            fflush(stdout);
        }

        count++;
        msleep(delay_ms);
    }

    fprintf(stdout, "\n\n");

    return count;
}

int read_adc(int fd)
{
    char buff[8];

    int val = ADC_READ_ERROR;

    memset(buff, 0, sizeof(buff));

    if (read(fd, buff, 8) < 0)
        perror("read()");
    else
        val = atoi(buff);

    return val;
}

int open_adc(int adc)
{
    char path[128];
    sprintf(path, "%sin%d_input", hwmonsyspath, adc);

    int fd = open(path, O_RDONLY);

    if (fd < 0) {
        perror("open()");
        printf("%s\n", path);
    }

    return fd;
}

void register_sig_handler()
{
    struct sigaction sia;

    bzero(&sia, sizeof sia);
    sia.sa_handler = sigint_handler;

    if (sigaction(SIGINT, &sia, NULL) < 0) {
        perror("sigaction(SIGINT)");
        exit(1);
    }
}

void sigint_handler(int sig)
{
    abort_read = 1;
}

void msleep(int ms)
{
    struct timespec ts;

    ts.tv_sec = ms / 1000;
    ts.tv_nsec = (ms % 1000) * 1000000;

    nanosleep(&ts, NULL);
}
