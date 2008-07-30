#!/usr/bin/python
"""
Handles finding command pads and listening for changes.
"""

import dbus

PAD_PRODUCT = 0x8000
PAD_VENDOR = 0x6A3
PAD_INTERFACE = 2

HAL_WKN = "org.freedesktop.Hal"
HAL_PRODUCT = "usb.product_id"
HAL_VENDOR = "usb.vendor_id"
HAL_INTERFACE = "usb.interface.number"
HAL_FILE = "input.device" # also "linux.device_file"
HAL_CAPABILITY = "input"
HAL_PARENT = "info.parent"


bus = None
def init():
	global bus
	bus = dbus.SystemBus()

def testDevice(dev):
	parent = dbus.Interface(bus.get_object(HAL_WKN, dev.GetProperty(HAL_PARENT)),
		'org.freedesktop.Hal.Device') 
	try:
		if parent.GetProperty(HAL_PRODUCT) != PAD_PRODUCT: return False
		if parent.GetProperty(HAL_VENDOR) != PAD_VENDOR: return False
		if parent.GetProperty(HAL_INTERFACE) != PAD_INTERFACE: return False
	except: return False
	else:
		return True

def getDeviceObjects():
	man = dbus.Interface(bus.get_object(HAL_WKN, "/org/freedesktop/Hal/Manager"), 
		'org.freedesktop.Hal.Manager')
	for dev in (dbus.Interface(bus.get_object(HAL_WKN, d), 'org.freedesktop.Hal.Device') 
	            for d in man.FindDeviceByCapability("input")):
		if testDevice(dev): yield dev

def getEventFiles():
	for dev in getDeviceObjects():
		try:
			yield dev.GetProperty(HAL_FILE)
		except: continue

def registerAddHandler(call):
	def _signal(dev):
		if not testDevice(dev): return
		try:
			call(dev.GetProperty(HAL_FILE))
		except: pass
	return bus.add_signal_receiver(_signal, 
		'DeviceAdded', 'org.freedesktop.Hal.Manager', HAL_WKN, '/org/freedesktop/Hal/Manager'
		)


def registerRemoveHandler(call):
	def _signal(dev):
		if not testDevice(dev): return
		try:
			call(dev.GetProperty(HAL_FILE))
		except: pass
	return bus.add_signal_receiver(_signal, 
		'DeviceRemoved', 'org.freedesktop.Hal.Manager', HAL_WKN, '/org/freedesktop/Hal/Manager'
		)

if __name__ == '__main__':
	init()
	for dev in getEventFiles():
		print dev
