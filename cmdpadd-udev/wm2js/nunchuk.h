#define WIIMOTE_EXTENSION_BUTTON_NUNCHUK_Z  0x01
#define WIIMOTE_EXTENSION_BUTTON_NUNCHUK_C  0x02


unsigned int ninty_decrypt(unsigned int encrypted);
int wiimote_input_extnunk(wiimote *wiimote, int uinput, int dataoffset);
