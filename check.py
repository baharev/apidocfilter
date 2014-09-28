from importlib import import_module
from inspect import getdoc

def attribs(name):
    mod = import_module(name)
    print name
    print 'Has __all__?', hasattr(mod, '__all__')    
    print 'Has __doc__?', hasattr(mod, '__doc__')
    print 'doc: ', getdoc(mod)

if __name__=='__main__':
    attribs('cairo')
    attribs('zope')
    attribs('A.B.C')
    
    import hacked
    class Object(object):
        pass
    
    opt = Object()
    opt.ignore_errors = False
    a, d = hacked.get_all_attr_has_docstr('/home/ali/ws-pydev/apidocfilter/A/B', 
                                         '/home/ali/ws-pydev/apidocfilter/A/B/C',
                                         opt)
    print(a)
    print(d)