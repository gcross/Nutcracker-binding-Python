#@+leo-ver=5-thin
#@+node:gcross.20110906104131.2847: * @file Nutcracker.py
#@@language python

#@+<< License >>
#@+node:gcross.20110906104131.3036: ** << License >>
#@+at
# Copyright (c) 2011, Gregory Crosswhite
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are permitted provided that the following conditions are met:
# 
#     * Redistributions of source code must retain the above copyright notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright notice, this list of conditions and the following disclaimer in the documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#@@c
#@-<< License >>

#@+<< Imports >>
#@+node:gcross.20110906104131.3052: ** << Imports >>
import ctypes
from ctypes import byref, c_char_p, c_uint32, POINTER
#@-<< Imports >>

#@+<< Initialize library bindings >>
#@+node:gcross.20110906104131.3053: ** << Initialize library bindings >>
c_complex_double = ctypes.c_double * 2
c_complex_double_p = POINTER(c_complex_double)

import ctypes.util

library = ctypes.cdll.LoadLibrary(ctypes.util.find_library("Nutcracker"))

clearError = library.Nutcracker_clearError
clearError.argtypes = []
clearError.restype = None

def getError():
    result = getError._c()
    if result:
        result = result.decode("utf-8")
    return None
getError._c = library.Nutcracker_getError
getError._c.argtypes = []
getError._c.restype = c_char_p

def setError(message):
    setError._c(message.encode("utf-8"))
setError._c = library.Nutcracker_setError
setError._c.argtypes = [c_char_p]
setError._c.restype = None

#@+others
#@-others
#@-<< Initialize library bindings >>

#@+others
#@+node:gcross.20110906130654.2872: ** Functions
#@+node:gcross.20110906130654.2875: *3* bind
def bind(name,argtypes,restype):
    function = getattr(library,name)
    function.argtypes = argtypes
    function.restype = restype
    def wrapped_function(*args):
        clearError()
        result = function(*args)
        message = getError()
        if(message):
            clearError()
            raise Exception(message)
        else:
            return result
    return staticmethod(wrapped_function)
#@+node:gcross.20110906130654.2873: *3* numpyBuffer
def numpyBuffer(arr):
    return ctypes.addressof(c_void_p.from_buffer(arr))
#@+node:gcross.20110906130654.2886: *3* toComplexDouble
def toComplexDouble(x):
    c = complex(x)
    return c_complex_double(c.real,c.imag)
#@+node:gcross.20110906130654.2885: *3* toComplexDoubleArray
def toComplexDoubleArray(data):
    return (c_complex_double * len(data))(*[toComplexDouble(x) for x in data])
#@+node:gcross.20110906104131.3054: ** Classes
#@+node:gcross.20110906104131.3055: *3* Vector
class Vector:
    #@+<< Bindings >>
    #@+node:gcross.20110906104131.3063: *4* << Bindings >>
    class C(ctypes.Structure): pass

    _add = bind("Nutcracker_Vector_add",[POINTER(C),POINTER(C)],POINTER(C))
    _free = bind("Nutcracker_Vector_free",[POINTER(C)],None)
    _getElementAtIndex = bind("Nutcracker_Vector_getElementAtIndex",[POINTER(C),c_uint32,c_complex_double_p],None)
    _getSize = bind("Nutcracker_Vector_getSize",[POINTER(C)],c_uint32)
    _multiply = bind("Nutcracker_Vector_multiply",[c_complex_double_p,POINTER(C)],POINTER(C))
    _new = bind("Nutcracker_Vector_new",[c_uint32,c_complex_double_p],POINTER(C))
    _newBasis = bind("Nutcracker_Vector_newBasis",[c_uint32,c_uint32],POINTER(C))

    dont_free = False
    #@-<< Bindings >>
    #@+others
    #@+node:gcross.20110906104131.3068: *4* __add__
    def __add__(self,other):
        assert(isinstance(other,Vector))
        return Vector(self._add(self._,other._))
    #@+node:gcross.20110906104131.3065: *4* __del__
    def __del__(self):
        if hasattr(self,"_"):
            if not self.dont_free:
                self._free(self._)
            del self._
    #@+node:gcross.20110906104131.3073: *4* __getitem__
    def __getitem__(self,index):
        data = c_complex_double()
        self._getElementAtIndex(self._,index,byref(data))
        return complex(*data)
    #@+node:gcross.20110906104131.3064: *4* __init__
    def __init__(self,*args):
        assert(len(args) == 1 or len(args) == 2)
        if(len(args)) == 2:
            self._ = self._newBasis(args[0],args[1])
        elif type(args[0]) == POINTER(Vector.C):
            self._ = args[0]
        else:
            data = toComplexDoubleArray(args[0])
            self._ = self._new(len(data),data)
    #@+node:gcross.20110906130654.2887: *4* __iter__
    def __iter__(self):
        for i in range(0,len(self)):
            yield self[i]
    #@+node:gcross.20110906104131.3072: *4* __len__
    def __len__(self):
        return int(self._getSize(self._))
    #@+node:gcross.20110906104131.3066: *4* __mul__
    def __mul__(self,c):
        return Vector(self._multiply(toComplexDouble(c),self._))
    #@+node:gcross.20110906130654.2889: *4* __reversed__
    def __reversed__(self):
        for i in reversed(range(0,len(self))):
            yield self[i]
    #@-others

#@+<< Constants >>
#@+node:gcross.20110906130654.2898: *4* << Constants >>
Vector.qubit_up = Vector(POINTER(Vector.C).in_dll(library,"Nutcracker_Vector_Qubit_Up"))
Vector.qubit_up.dont_free = True

Vector.qubit_down = Vector(POINTER(Vector.C).in_dll(library,"Nutcracker_Vector_Qubit_Down"))
Vector.qubit_down.dont_free = True
#@-<< Constants >>
#@-others

#@+<< Export list >>
#@+node:gcross.20110906104131.3062: ** << Export list >>
__all__ = [
    "library",
    "clearError",
    "getError",
    "setError",
    "Vector",
]
#@-<< Export list >>
#@-leo
