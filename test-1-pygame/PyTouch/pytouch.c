#include <linux/input.h>
#include <string.h>
#include <fcntl.h>
#include <stdio.h>
#include "touch.h"
#include "touch.c"
#include <signal.h>
#include <stdlib.h>
#include <unistd.h>
#include <pthread.h>

#define SAMPLE_AMOUNT 1
#define DEFAULT_SCREEN_WIDTH 480
#define DEFAULT_SCREEN_HEIGHT 320

pthread_t thread = NULL;

void  INThandler(int sig)
{
        signal(sig, SIG_IGN);
	pthread_cancel(thread);
        exit(0);
}

void* keepaliveThread(void *arg)
{
	printf("TIMER STARTED\n");
	int* t_ptr = (int *)arg;
	while(1)
	{
		sleep(*t_ptr);
		printf("KEEPALIVE\n");
	}
	return NULL;
}

int main(int argc, char *argv[])
{
	setvbuf(stdout, (char *) NULL, _IOLBF, 0); /* make line buffered stdout */
	signal(SIGINT, INThandler);

	int xres, yres;

	int Xsamples[20];
	int Ysamples[20];

	int screenXmax, screenXmin;
	int screenYmax, screenYmin;

	int rawX, rawY, rawPressure, scaledX, scaledY;

	int Xaverage = 0;
	int Yaverage = 0;
	int keepalive = 1; //Keepalive timer

	if (openTouchScreen() == 1)
	{
		printf("ERROR: Error reading touchscreen.\n");
		return 1;
	}

	getTouchScreenDetails(&screenXmin,&screenXmax,&screenYmin,&screenYmax);

	if (argc < 3)
	{
		xres = DEFAULT_SCREEN_WIDTH;
		yres = DEFAULT_SCREEN_HEIGHT;
	}
	else
	{
		xres = atoi(argv[1]);
		yres = atoi(argv[2]);
	}
	if (argc >= 4)
	{
		//Add specific device
	}
	if (argc >= 5)
	{
		keepalive = atoi(argv[5]);
	}

	if (keepalive > 0)
	{
		if (pthread_create(&thread, NULL, keepaliveThread, &keepalive))
		{
			printf("ERROR: Cannot create keepalive thread");
			return 1;
		}
	}

	//scaleXvalue = ((float)screenXmax-screenXmin) / xres;
	//scaleYvalue = ((float)screenYmax-screenYmin) / yres;

	int sample, x;

	printf("INIT: SUCCESS!\n");

	while(1){
		for (sample = 0; sample < SAMPLE_AMOUNT; sample++){
			getTouchSample(&rawX, &rawY, &rawPressure);
			Xsamples[sample] = rawX;
			Ysamples[sample] = rawY;
		}

		Xaverage  = 0;
		Yaverage  = 0;

		for ( x = 0; x < SAMPLE_AMOUNT; x++ ){
			Xaverage += Xsamples[x];
			Yaverage += Ysamples[x];
		}

		Xaverage = Xaverage/SAMPLE_AMOUNT;
		Yaverage = Yaverage/SAMPLE_AMOUNT;

		scaledX = (int)(((float)Xaverage - (float)screenXmin)/((float)screenXmax-(float)screenXmin)*((float)xres));
		scaledY = (int)(((float)Yaverage - (float)screenYmin)/((float)screenYmax-(float)screenYmin)*((float)yres));

		//scaledX = 	Xaverage / scaleXvalue;
		//scaledY = 	Yaverage / scaleYvalue;
		printf ("TOUCH: %i %i\n", scaledX, scaledY);
//		drawSquare(scaledX, scaledY,5,5,WHITE);
	}
}


