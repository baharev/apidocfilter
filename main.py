from __future__ import print_function
import imp
import inspect

#from sphinx.util.inspect import getargspec, isdescriptor, safe_getmembers

def main():
    code = 'from %s import *' % 'pkg.another_module' # 'some_module' 
    module = imp.new_module('someFakeName')
    exec code in module.__dict__
    #
    # This one seems OK for package imports:
    print('* __dict__')
    print([n for n in module.__dict__ if not n.startswith('_')])
    #
    # And this one for modules 
    print('* inspect') 
    for name, obj in inspect.getmembers(module):
        if inspect.isfunction(obj) or inspect.isclass(obj):
            print(name)
    #
    print('* dir()')    
    print([n for n in dir(module) if not n.startswith('_')])
    #
    print('* Sphinx')
    if hasattr(module, '__all__'):
        print(module.__all__)
    else:
        pass
    


if __name__ == '__main__':
    main()