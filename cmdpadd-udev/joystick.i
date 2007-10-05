// vim:syn=c
%module joystick
%feature("autodoc", "1");

#ifndef SWIGPYTHON
#error "Doesn't work except with Python"
#endif

%{
/* Put headers and other declarations here */
#include <linux/joystick.h>
%}

/*%typemap(in) __time_t {
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
}*/

typedef signed char __s8;
typedef unsigned char __u8;
typedef signed int __s16;
typedef unsigned int __u16;
typedef signed long int __s32;
typedef unsigned long int __u32;

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

%include <linux/joystick.h>

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

STRUCT_UTILS(JS_DATA_SAVE_TYPE_32);
STRUCT_UTILS(JS_DATA_SAVE_TYPE_64);
STRUCT_UTILS(JS_DATA_TYPE);
STRUCT_UTILS(js_corr);
STRUCT_UTILS(js_event);

%define RAW_CONST(type, name)
%init %{
SWIG_Python_SetConstant(d, #name,SWIG_From_##type((type)(name)));
%}
%pythoncode %{
globals()[`name`] = getattr(_joystick, `name`)
%}
%enddef

RAW_CONST(long, JSIOCGVERSION);

RAW_CONST(long, JSIOCGAXES);
RAW_CONST(long, JSIOCGBUTTONS);

RAW_CONST(long, JSIOCSCORR);
RAW_CONST(long, JSIOCGCORR);

RAW_CONST(long, JSIOCSAXMAP);
RAW_CONST(long, JSIOCGAXMAP);
RAW_CONST(long, JSIOCSBTNMAP);
RAW_CONST(long, JSIOCGBTNMAP);

RAW_CONST(long, JS_RETURN);

long _JSIOCGNAME(long len);

%pythoncode %{
def JSIOCGNAME(*args):
  """JSIOCGNAME(long len) -> long"""
  return _joystick._JSIOCGNAME(*args)
%}

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
    SWIG_init();
}

long _JSIOCGNAME(long len) {
	return JSIOCGNAME(len);
}
%}
