#include "uinput.h"
#include "wiimote.h"
#include "wm2js.h"
#include <fcntl.h>
#include <string.h>
#include <sys/ioctl.h>
#include <unistd.h>

/* Create uinput output */
int do_uinput(int fd, unsigned short key, int pressed, unsigned short event_type) {
	struct uinput_event event;
	memset(&event, 0 , sizeof(event));
	
	event.type = event_type;
	event.code = key;
	event.value = pressed;
	
	if(write(fd,&event,sizeof(event)) != sizeof(event))
		xxxdie("Writing event to uinput driver failed ; Aborting");
	return TRUE;
}


/* Init uinput */
int init_uinput_device(void) {
	struct uinput_dev dev;
	int fd = -1;
	
	fd = open("/dev/input/uinput", O_RDWR);
	if(fd < 0)
		fd = open("/dev/misc/uinput", O_RDWR);

	if(fd < 0) {
		xxxwarn("Unable to open uinput device ; hint: 'modprobe uinput' ?!");
		return -1;
	}
	
	memset(&dev,0,sizeof(dev));
	strncpy(dev.name, "WiiMote", UINPUT_MAX_NAME_SIZE);
	dev.idbus     = 0;
	dev.idvendor  = WIIMOTE_VENDOR;
	dev.idproduct = WIIMOTE_PRODUCT;
	dev.idversion = 0x01;

	if(write(fd, &dev, sizeof(dev)) < sizeof(dev)) {
		xxxwarn("Registering device at uinput failed");
		return -1;
	}
	ioctl(fd, UI_SET_EVBIT, EV_ABS)        && xxxdie("Can't set EV_ABS"); /* Joydev */
	ioctl(fd, UI_SET_EVBIT, EV_KEY)        && xxxdie("Can't set EV_KEY"); /* Keys */
	ioctl(fd, UI_SET_ABSBIT, ABS_X)        && xxxdie("Can't set ABS_X");  /* + */
	ioctl(fd, UI_SET_ABSBIT, ABS_Y)        && xxxdie("Can't set ABS_Y");
	
	ioctl(fd, UI_SET_ABSBIT, ABS_RX)       && xxxdie("Can't set ABS_RX"); /* Motion sensor */
	ioctl(fd, UI_SET_ABSBIT, ABS_RY)       && xxxdie("Can't set ABS_RY");
	ioctl(fd, UI_SET_ABSBIT, ABS_RZ)       && xxxdie("Can't set ABS_RZ");

	ioctl(fd, UI_SET_ABSBIT, ABS_HAT0X)       && xxxdie("Can't set ABS_RZ"); /* Nunchuck joystick */
	ioctl(fd, UI_SET_ABSBIT, ABS_HAT0Y)       && xxxdie("Can't set ABS_RZ");

	ioctl(fd, UI_SET_KEYBIT, BTN_TOP2)     && xxxdie("Can't set BTN_TOP2");
	ioctl(fd, UI_SET_KEYBIT, BTN_BASE)     && xxxdie("Can't set BTN_BASE");
	ioctl(fd, UI_SET_KEYBIT, BTN_BASE2)    && xxxdie("Can't set BTN_BASE2");
	ioctl(fd, UI_SET_KEYBIT, BTN_TRIGGER)  && xxxdie("Can't set BTN_TRIGGER");
	ioctl(fd, UI_SET_KEYBIT, BTN_THUMB)    && xxxdie("Can't set BTN_THUMB");
	ioctl(fd, UI_SET_KEYBIT, BTN_TOP)      && xxxdie("Can't set BTN_TOP");
	ioctl(fd, UI_SET_KEYBIT, BTN_BASE3)    && xxxdie("Can't set BTN_BASE3");
	ioctl(fd, UI_SET_KEYBIT, BTN_BASE5)    && xxxdie("Can't set BTN_BASE5");
	ioctl(fd, UI_SET_KEYBIT, BTN_BASE6)    && xxxdie("Can't set BTN_BASE6");
	ioctl(fd, UI_DEV_CREATE)               && xxxdie_i("Unable to create device on fd ",fd);
	return fd;
}
