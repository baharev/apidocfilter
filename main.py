from __future__ import print_function
import imp
import inspect

FAKE_NAME = '__noSuchName__'
            
def members_to_doc(module_path):
    module = imp.load_source(FAKE_NAME, module_path)
    return getattr(module, '__all__', get_members_to_doc(module))

def get_members_to_doc(module):
    to_doc = [ ]
    for name, obj in inspect.getmembers(module):
        if not_hidden(name) and is_in_module(obj):
            to_doc.append(name)
    return to_doc

def not_hidden(name):
    return not name.startswith('_')

def is_in_module(obj):
    # Filter out implicitly imported members
    return getattr(obj, '__module__', '') == FAKE_NAME

def main():
    module_path = './pkg/another_module.py'
    module = imp.load_source(FAKE_NAME, module_path)
    #
    print('* inspect') 
    for name, obj in inspect.getmembers(module):
        # if not name.startswith('_') !!!
        if inspect.isfunction(obj) or inspect.isclass(obj):
            print(name, '(%s)' % obj.__module__)
    #
    print('* __all__')
    if hasattr(module, '__all__'):
        print(module.__all__)
    else:
        print('does not have __all__')
    #
    print('* to document')
    print(members_to_doc(module_path))

if __name__ == '__main__':
    import apidoc
    apidoc.main()
