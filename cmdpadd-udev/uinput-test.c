#include <linux/input.h>
#include <linux/uinput.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <sys/fcntl.h>
#include <stdio.h>
#include <errno.h>
#include <unistd.h>
#include <string.h>

// Many thanks to pab- in #wiidev on EFnet for getting this to work.

#define CHECK(func) en = errno; \
printf(#func "(): rv=%i errno=%i\n", rv, en); \
if (en != 0) { \
	printf("ERROR: %i: %s\n", errno, strerror(errno)); \
	return en; \
}

int main(int argc, char** argv)
{
	struct uinput_user_dev dev;
	struct input_event z;
	int rv, en;
	// Initialize device
	int fd = rv = open("/dev/input/uinput", O_WRONLY | O_NDELAY);
	CHECK(open);
	memset(&dev,0,sizeof(dev));
	// Meant to imitate the device I'll eventually filter
	strncpy(dev.name, "Saitek Magic Bus", UINPUT_MAX_NAME_SIZE);
	dev.id.bustype = 0;
	dev.id.vendor  = 0x06A3;
	dev.id.product = 0x8000;
	dev.id.version = 0x0111;

	rv = write(fd, &dev, sizeof(dev));
	CHECK(write);
	
	// You need to "declare" all the events you will send.
	rv = ioctl(fd, UI_SET_EVBIT, EV_KEY); // Sending a "Key" type event
	CHECK(ioctl);
	rv = ioctl(fd, UI_SET_KEYBIT, KEY_ENTER); // ... with a code of "Enter"
	CHECK(ioctl);
	
	ioctl(fd, UI_DEV_CREATE);
	CHECK(ioctl);
	
	sleep(10);
	
	// then to send the event
	memset(&z,0,sizeof(z));
	z.type = EV_KEY;
	z.code = KEY_ENTER;  // for example; other codes are in the kernel uinput.h
	z.value = 1;
	rv = write(fd, &z, sizeof(z));
	CHECK(write);
	
	z.value = 0;
	rv = write(fd, &z, sizeof(z));
	CHECK(write);
	
	// Uninit device
	ioctl(fd, UI_DEV_DESTROY);
	rv = close(fd);
	CHECK(close);
	return 0;
}

