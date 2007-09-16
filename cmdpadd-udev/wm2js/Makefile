CC      = gcc
CFLAGS  = -Wall -O -g
LIBS    = -lbluetooth
SRCS    = nunchuk.c  uinput.c  wiimote.c  wm2js.c
OBJS    = $(SRCS:.c=.o)
MAIN    = wm2js


.PHONY: depend clean

all:		$(MAIN)

$(MAIN):	$(OBJS) 
		$(CC) $(CFLAGS) $(INCLUDES) -o $(MAIN) $(OBJS) $(LFLAGS) $(LIBS)

.c.o:
		$(CC) $(CFLAGS) $(INCLUDES) -c $<

clean:
		$(RM) *.o *~ $(MAIN)

depend: 	$(SRCS)
		makedepend $(INCLUDES) $^

# DO NOT DELETE THIS LINE -- make depend needs it
