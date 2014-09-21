from __future__ import print_function
import imp
import importlib
import os
import sys
import traceback

# The goal is to return __all__ from __init__.py if __all__ is present, and 
# return None otherwise. It is safe to assume that __init__.py exists.

def get_all_from_initpy(path):
    initpy_path = os.path.join(path,'__init__.py')
    assert os.path.isfile(initpy_path), path
    try:
        module = imp.load_source('__a_hopefully_unique_name__', initpy_path)
        return getattr(module, '__all__', None)
    except:
        print(traceback.format_exc())
        print('imp.load_source failed for',initpy_path)
        #sys.exit(1)
        
def get_all_attrib(path, package):
    initpy_path = os.path.join(path,'__init__.py')
    assert os.path.isfile(initpy_path), path
    try:
        sys.path.append(path)
        module = importlib.import_module('__init__', package)
        all_mods = getattr(module, '__all__', None)
        del sys.modules['__init__'] 
        return all_mods
    except:
        print(traceback.format_exc())
        print('importlib.import_module failed for',initpy_path)
        #sys.exit(1)
    finally:
        sys.path.remove(path)

def main():
    print(get_all_from_initpy('/usr/lib/python2.7/xml'))
    print('--------------------------------------------------------------')
    print(get_all_attrib('/usr/lib/python2.7/xml', 'xml'))    
    print('--------------------------------------------------------------')
    get_all_from_initpy('/usr/lib/python2.7/unittest')
    print('--------------------------------------------------------------')
    get_all_attrib('/usr/lib/python2.7/unittest', 'unittest')      
        
if __name__ == '__main__':
    main()