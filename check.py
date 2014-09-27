from importlib import import_module

def attribs(name):
    mod = import_module(name)
    print name
    print 'Has __all__?', hasattr(mod, '__all__')    
    print 'Has __doc__?', hasattr(mod, '__doc__')
    print(getattr(mod, '__doc__'))

if __name__=='__main__':
    attribs('cairo')
    attribs('zope')