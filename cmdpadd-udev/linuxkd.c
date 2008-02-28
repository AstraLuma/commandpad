#include <Python.h>
#include <linux/kd.h>
#include <sys/ioctl.h>
#include <errno.h>

static PyObject *
linuxkd_getled(PyObject *self, PyObject *args)
{
	int fd, led, rv;
	unsigned long value;
	
	if (!PyArg_ParseTuple(args, "ii:getled", &fd, &led))
		return NULL;
	
	if (led != LED_CAP && led != LED_NUM && led != LED_SCR)
	{
		PyErr_SetString(PyExc_ValueError, "Second argument must be LED_CAP, LED_NUM, or LED_SCR");
		return NULL;
	}
	
	Py_BEGIN_ALLOW_THREADS
	rv = ioctl(fd, KDGETLED, &value);
	Py_END_ALLOW_THREADS
	
	if (rv == -1)
	{
		PyErr_SetFromErrno(PyExc_IOError);
		return NULL;
	}
	
	return PyBool_FromLong(value & led);
}

static PyObject *
linuxkd_setled(PyObject *self, PyObject *args)
{
	int fd, led, rv, bval;
	unsigned long value;
	
	if (!PyArg_ParseTuple(args, "iii:setled", &fd, &led, &bval))
		return NULL;
	
	if (led != LED_CAP && led != LED_NUM && led != LED_SCR)
	{
		PyErr_SetString(PyExc_ValueError, "Second argument must be LED_CAP, LED_NUM, or LED_SCR");
		return NULL;
	}
	
	// The point of this is to minimize the race condition between KDGETLED and KDSETLED
	// If the race condition fails, then someone's changes are trashed.
	Py_BEGIN_ALLOW_THREADS
	rv = ioctl(fd, KDGETLED, &value); // Begin race
	if (rv != -1)
	{
		value &= ~led;
		if (bval) value |= led;
		rv = ioctl(fd, KDSETLED, &value); // End race
	}
	Py_END_ALLOW_THREADS
	
	if (rv == -1)
	{
		PyErr_SetFromErrno(PyExc_IOError);
		return NULL;
	}
	
	Py_RETURN_NONE;
}

static PyMethodDef LinuxkdMethods[] = {
	{"getled",  linuxkd_getled, METH_VARARGS, "getled(fd, led)\nGets a given LED"},
	{"setled",  linuxkd_setled, METH_VARARGS, "setled(fd, led, value)\nSets a given LED"},
	{NULL, NULL, 0, NULL}        /* Sentinel */
};

PyMODINIT_FUNC
initlinuxkd(void)
{
	PyObject *m;
	
	m = Py_InitModule("linuxkd", LinuxkdMethods);
	if (m == NULL)
		return;
	
	PyModule_AddIntConstant(m, "LED_CAP", LED_CAP);
	PyModule_AddIntConstant(m, "LED_NUM", LED_NUM);
	PyModule_AddIntConstant(m, "LED_SCR", LED_SCR);
}

