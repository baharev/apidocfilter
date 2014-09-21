from __future__ import print_function
import importlib, os, sys
# The goal is to return __all__ from __init__.py if __all__ is present, and 
# return None otherwise. It is safe to assume that __init__.py exists.

def get_all_attrib(path):
    try:
        sys.path.append(path)
        pkg = os.path.basename(path)
        before = set(sys.modules)
        module = importlib.import_module(pkg, package=pkg)
        difference  = sys.modules.viewkeys() - before
        #print('difference =', str(difference))
        all_attrib = getattr(module, '__all__', None)
        for k in difference:
            sys.modules.pop(k)
        return all_attrib
    finally:
        sys.path.remove(path)

if __name__ == '__main__':
    print(get_all_attrib('/home/ali/ws-pydev/apidocfilter/pkg')) 
    print(get_all_attrib('/usr/lib/python2.7/xml'))    
    print(get_all_attrib('/usr/lib/python2.7/unittest'))      
