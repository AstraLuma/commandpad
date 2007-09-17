// vim:syn=c
%module uinput
%feature("autodoc", "1");

#ifndef SWIGPYTHON
#error "Doesn't work except with Python"
#endif

%{
/* Put headers and other declarations here */
#include <linux/input.h>
#include <linux/uinput.h>
%}

%typemap(in) __time_t {
    $1 = PyLong_AsLong($input);
}
%typemap(out) __time_t {
    $result = PyLong_FromLong($1);
}

%typemap(in) __suseconds_t {
    $1 = PyLong_AsLong($input);
}
%typemap(out) __suseconds_t {
    $result = PyLong_FromLong($1);
}

%typemap(in) __u16 {
    $1 = PyLong_AsUnsignedLong($input);
}
%typemap(out) __u16 {
	PyObject * spam = 0;
	spam = PyLong_FromUnsignedLong($1);
    $result = PyLong_FromUnsignedLong($1);
}

typedef signed long int __s32;

// This does not create the cleanest wrapper (I'd rather a dynamic-updater with 
// a custom class), but it works.

%typemap(in) int[ANY](int temp[$1_dim0]) {
  int i;
  if (!PySequence_Check($input)) {
      PyErr_SetString(PyExc_TypeError,"Expecting a sequence");
      return NULL;
  }
  if (PyObject_Length($input) != $1_dim0) {
      PyErr_SetString(PyExc_ValueError,"Expecting a sequence with $1_dim0 elements");
      return NULL;
  }
  for (i = 0; i < $1_dim0; i++) {
      PyObject *o = PySequence_GetItem($input,i);
      if (!PyInt_Check(o)) {
         Py_XDECREF(o);
         PyErr_SetString(PyExc_ValueError,"Expecting a sequence of ints");
         return NULL;
      }
      temp[i] = PyInt_AsLong(o);
      Py_DECREF(o);
  }
  $1 = &temp[0];
}

%typemap(out) int[ANY](int temp[$1_dim0]) {
  int i;
  $result = PyTuple_New($1_dim0);
  for (i = 0; i < $1_dim0; i++) {
    PyTuple_SetItem($result, i, PyInt_FromLong($1[i]));
  }
}

%include <linux/input.h>
%include <linux/uinput.h>

struct timeval
{
    __time_t tv_sec;		/* Seconds.  */
    __suseconds_t tv_usec;	/* Microseconds.  */
};

%define STRUCT_UTILS(type)
%extend type {
	PyObject* pack() {
		char* rv = 0;
		rv = malloc(sizeof(struct type));
		memcpy(rv, $self, sizeof(struct type));
		return PyString_FromStringAndSize(rv, sizeof(struct type));
	}
	
	static struct type *unpack(PyObject *data) {
		struct type *rv = 0;
		if (!PyString_Check(data) || PyString_Size(data) != sizeof(struct type)) {
			return NULL;
		}
		rv = malloc(sizeof(struct type));
		//printf("type::unpack:rv:%x\n", rv);
		memcpy(rv, PyString_AsString(data), sizeof(struct type));
		return rv;
	}
	
	static size_t length() {
		return sizeof(struct type);
	}
}
%newobject type::pack;
%newobject type::unpack;
%exception type::unpack {
  $action
  if (!result) {
     PyErr_SetString(PyExc_ValueError,"Expecting a string of the correct length");
     return NULL;
  }
}
%enddef

STRUCT_UTILS(ff_condition_effect);
STRUCT_UTILS(ff_constant_effect);
STRUCT_UTILS(ff_effect);
// ff_effect_u is a union in ff_effect
STRUCT_UTILS(ff_envelope);
STRUCT_UTILS(ff_periodic_effect);
STRUCT_UTILS(ff_ramp_effect);
STRUCT_UTILS(ff_replay);
STRUCT_UTILS(ff_rumble_effect);
STRUCT_UTILS(ff_trigger);
STRUCT_UTILS(input_absinfo);
STRUCT_UTILS(uinput_ff_erase);
STRUCT_UTILS(uinput_ff_upload);
STRUCT_UTILS(input_id);
STRUCT_UTILS(timeval);
STRUCT_UTILS(input_event);
STRUCT_UTILS(uinput_user_dev);


%define RAW_CONST(type, name)
%init %{
SWIG_Python_SetConstant(d, #name,SWIG_From_##type((type)(name)));
%}
%pythoncode %{
globals()[`name`] = getattr(_uinput, `name`)
%}
%enddef

    RAW_CONST(long, UI_SET_EVBIT);
    RAW_CONST(long, UI_SET_KEYBIT);
    RAW_CONST(long, UI_SET_RELBIT);
    RAW_CONST(long, UI_SET_ABSBIT);
    RAW_CONST(long, UI_SET_MSCBIT);
    RAW_CONST(long, UI_SET_LEDBIT);
    RAW_CONST(long, UI_SET_SNDBIT);
    RAW_CONST(long, UI_SET_FFBIT);
    RAW_CONST(long, UI_SET_PHYS);
    RAW_CONST(long, UI_SET_SWBIT);
    RAW_CONST(long, UI_DEV_CREATE);
    RAW_CONST(long, UI_DEV_DESTROY);

%{
// Some forward declarations
#ifdef __cplusplus
extern "C"
#endif
SWIGEXPORT void SWIG_init(void);

static PyMethodDef SwigMethods[];

PyMODINIT_FUNC
inituinput(void)
{
    PyObject *m, *d;
    
    m = Py_InitModule("uinput",SwigMethods);
    if (m == NULL)
       return;
    SWIG_init();
    
    d = PyModule_GetDict(m);

/*#define CONST(c) SWIG_Python_SetConstant(d, #c,SWIG_From_long((long)(c)))
// SWIG gets confused on these
    CONST(UI_SET_EVBIT);
    CONST(UI_SET_KEYBIT);
    CONST(UI_SET_RELBIT);
    CONST(UI_SET_ABSBIT);
    CONST(UI_SET_MSCBIT);
    CONST(UI_SET_LEDBIT);
    CONST(UI_SET_SNDBIT);
    CONST(UI_SET_FFBIT);
    CONST(UI_SET_PHYS);
    CONST(UI_SET_SWBIT);
    CONST(UI_DEV_CREATE);
    CONST(UI_DEV_DESTROY);
#undef CONST*/
}
%}

/*%pythoncode %{
UI_SET_EVBIT = _uinput.UI_SET_EVBIT
UI_SET_KEYBIT = _uinput.UI_SET_KEYBIT
UI_SET_RELBIT = _uinput.UI_SET_RELBIT
UI_SET_ABSBIT = _uinput.UI_SET_ABSBIT
UI_SET_MSCBIT = _uinput.UI_SET_MSCBIT
UI_SET_LEDBIT = _uinput.UI_SET_LEDBIT
UI_SET_SNDBIT = _uinput.UI_SET_SNDBIT
UI_SET_FFBIT = _uinput.UI_SET_FFBIT
UI_SET_PHYS = _uinput.UI_SET_PHYS
UI_SET_SWBIT = _uinput.UI_SET_SWBIT
UI_DEV_CREATE = _uinput.UI_DEV_CREATE
UI_DEV_DESTROY = _uinput.UI_DEV_DESTROY
%}
*/
