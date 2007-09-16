#include "uinput.h"
#include "wiimote.h"
#include "nunchuk.h"
#include "wm2js.h"

/* Decrypt Zero-Key data from Extension-Device */
unsigned int ninty_decrypt(unsigned int encrypted) {
	unsigned int decrypted;
	decrypted = ((encrypted ^ 0x17)+17)&0xFF;
	return decrypted;
}

/* Parse Extension-Data from a NunChuk */
int wiimote_input_extnunk(wiimote *wiimote, int uinput, int dataoffset) {

	unsigned int btn_cz;
	unsigned int i,dochange;
	unsigned int current_bitmask = 0;
	unsigned int updown = 0;
	
	/* Send Joystick events to uinput */
	do_uinput(uinput,ABS_HAT0X,ninty_decrypt(wiimote->payload[dataoffset]), EV_ABS);
	do_uinput(uinput,ABS_HAT0Y,ninty_decrypt(wiimote->payload[dataoffset+1]), EV_ABS);
	
	/* Grab bitmask for C and Z */
	btn_cz = ninty_decrypt(wiimote->payload[dataoffset+5]);
	
	/* .. and cure some stupidity .. */
	current_bitmask = (((btn_cz & WIIMOTE_EXTENSION_BUTTON_NUNCHUK_Z) ? 0 : 1) + (btn_cz & WIIMOTE_EXTENSION_BUTTON_NUNCHUK_C));
	
	for(i=WIIMOTE_EXTENSION_BUTTON_NUNCHUK_Z; i<=WIIMOTE_EXTENSION_BUTTON_NUNCHUK_C; (i = i*2)) {
		dochange = 0;
		if((current_bitmask & i ) && !(wiimote->extbitmask_nunchuk & i)) {
			updown=1; dochange=1;
		}
		else if((!(current_bitmask & i )) && (wiimote->extbitmask_nunchuk & i)) {
			updown=0; dochange=1;
		}
		
		if(dochange) {
			switch(i) {
				case WIIMOTE_EXTENSION_BUTTON_NUNCHUK_Z:
					do_uinput(uinput,BTN_BASE5,updown,EV_KEY);
					break;
				case WIIMOTE_EXTENSION_BUTTON_NUNCHUK_C:
					do_uinput(uinput,BTN_BASE6,updown,EV_KEY);
					break;
				default:
					xxxdie_i("Unknown NUNCHUK button ",i);
			};
		}
	}
	
	/* Store bitmask */
	wiimote->extbitmask_nunchuk = current_bitmask;
	return TRUE;
}

