#include <linux/input.h>
#include <string.h>
#include <fcntl.h>
#include <stdio.h>
#include "touch.h"
#include "touch.c"
#include "framebuffer.c"
#include <signal.h>


#define SAMPLE_AMOUNT 2
#define SCREEN_WIDTH 480
#define SCREEN_HEIGHT 320

void  INThandler(int sig)
{
        signal(sig, SIG_IGN);
        exit(0);
}

int main()
{
	signal(SIGINT, INThandler);

	int xres, yres, x;

	int Xsamples[20];
	int Ysamples[20];

	int screenXmax, screenXmin;
	int screenYmax, screenYmin;

	float scaleXvalue, scaleYvalue;

	int rawX, rawY, rawPressure, scaledX, scaledY;


	if (openTouchScreen() == 1)
		perror("ERROR\nError opening touchscreen");

	getTouchScreenDetails(&screenXmin,&screenXmax,&screenYmin,&screenYmax);

	xres = SCREEN_WIDTH;
	yres = SCREEN_HEIGHT;

	
}


