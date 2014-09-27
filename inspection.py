from __future__ import print_function
from importlib import import_module
import inspect
            
# Package inspection            
            
def members_to_doc(pkgname):
    module = import_module(pkgname)
    return getattr(module, '__all__', get_members_to_doc(module,pkgname))

def get_members_to_doc(module,pkgname):
    to_doc = [ ]
    for name, obj in inspect.getmembers(module):
        # There will be __doc__ with obj either being str or NoneType
        if not_hidden(name) and is_in_module(obj,pkgname):
            to_doc.append(name)
    return to_doc

def not_hidden(name):
    return True
    #return not name.startswith('_')

def is_in_module(obj,pkgname):
    modname = getattr(obj, '__module__', '') 
    print(modname)
    return modname == pkgname

def main():
    print('* to document')
    print(members_to_doc('A.B.C'))

if __name__ == '__main__':
    main()