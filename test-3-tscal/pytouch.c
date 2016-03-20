#include <linux/input.h>
#include <string.h>
#include <fcntl.h>
#include <stdio.h>
#include "touch.h"
#include "touch.c"
#include <signal.h>
#include <stdlib.h>

#define SAMPLE_AMOUNT 1
#define DEFAULT_SCREEN_WIDTH 480
#define DEFAULT_SCREEN_HEIGHT 320

void  INThandler(int sig)
{
        signal(sig, SIG_IGN);
        exit(0);
}

int main(int argc, char *argv[])
{
	signal(SIGINT, INThandler);

	int xres, yres;

	int Xsamples[20];
	int Ysamples[20];

	int screenXmax, screenXmin;
	int screenYmax, screenYmin;

	int rawX, rawY, rawPressure, scaledX, scaledY;

	int Xaverage = 0;
	int Yaverage = 0;


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


