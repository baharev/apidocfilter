from __future__ import print_function
import sys, importlib, os
import traceback as tb

def get_all_attribute():
    #path = '/usr/lib/python2.7/dist-packages/scipy/sparse/linalg/isolve'
    path = '/home/ali/ws-pydev/apidocfilter/A/B'
    assert os.path.isdir(path)
    try:
        path_before = list(sys.path)
        modules_before = set(sys.modules)
        #head, pkg = os.path.split(path) # How does this play with hierarchical packages?
        #sys.path = [head] + sys.path # FIXME Prepend or append?
        #module = importlib.import_module('scipy.sparse.linalg.isolve')
        sys.path = sys.path + ['/home/ali/ws-pydev/apidocfilter/A']
        module = importlib.import_module('B.C')        
        return getattr(module, '__all__', None)
    except:
        print('\n', tb.format_exc()[:-1],file=sys.stderr)         
        print('Please make sure that',path,'can be imported',
              '(or exclude this path).', file=sys.stderr)
#       sys.exit(1)        # FIXME Or a --sloppy option?
    finally:
        difference = sys.modules.viewkeys() - modules_before        
        for k in difference:
            sys.modules.pop(k)
        sys.path = path_before

def main():
    print(get_all_attribute())
        
if __name__ == '__main__':
    main()