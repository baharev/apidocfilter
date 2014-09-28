# -*- coding: utf-8 -*-
"""
    sphinx.apidoc
    ~~~~~~~~~~~~~

    Parses a directory tree looking for Python modules and packages and creates
    ReST files appropriately to create code documentation with Sphinx.  It also
    creates a modules index (named modules.<suffix>).

    This is derived from the "sphinx-autopackage" script, which is:
    Copyright 2008 Société des arts technologiques (SAT),
    http://www.sat.qc.ca/

    :copyright: Copyright 2007-2014 by the Sphinx team, see AUTHORS.
    :license: BSD, see LICENSE for details.
"""
from __future__ import print_function

import importlib
import os
import string
import sys
import optparse
import traceback as tb
from os.path import join

from sphinx.util.osutil import walk
from sphinx import __version__

# automodule options
if 'SPHINX_APIDOC_OPTIONS' in os.environ:
    OPTIONS = os.environ['SPHINX_APIDOC_OPTIONS'].split(',')
else:
    OPTIONS = [
        'members',
        'undoc-members',
        # 'inherited-members', # disabled because there's a bug in sphinx
        'show-inheritance',
    ]

INITPY = '__init__.py'
PY_SUFFIXES = set(['.py', '.pyx'])


def makename(package, module):
    """Join package and module with a dot."""
    # Both package and module can be None/empty.
    if package:
        name = package
        if module:
            name += '.' + module
    else:
        name = module
    return name


def write_file(name, text, opts):
    """Write the output file for module/package <name>."""
    fname = join(opts.destdir, '%s.%s' % (name, opts.suffix))
    if opts.dryrun:
        # FIXME --quiet option?
        # wrap the print function
        print('Would create file %s.' % fname)
        return
    if not opts.force and os.path.isfile(fname):
        #print('File %s already exists, skipping.' % fname)
        pass
    else:
        #print('Creating file %s.' % fname)
        f = open(fname, 'w')
        try:
            f.write(text)
        finally:
            f.close()


def format_heading(level, text):
    """Create a heading of <level> [1, 2 or 3 supported]."""
    underlining = ['=', '-', '~', ][level - 1] * len(text)
    return '%s\n%s\n\n' % (text, underlining)


def format_directive(module, package=None):
    """Create the automodule directive and add the options."""
    directive = '.. automodule:: %s\n' % makename(package, module)
    for option in OPTIONS:
        directive += '    :%s:\n' % option
    return directive


def create_module_file(package, module, opts):
    """Build the text of the file and write the file."""
    if not opts.noheadings:
        text = format_heading(1, '%s module' % module)
    else:
        text = ''
    #text += format_heading(2, ':mod:`%s` Module' % module)
    text += format_directive(module, package)
    write_file(makename(package, module), text, opts)


def create_package_file(master_package, subroot, submods, opts, subs):
    """Build the text of the file and write the file."""
    text = format_heading(1, '%s package' % makename(master_package, subroot))

    if opts.modulefirst:
        text += format_directive(subroot, master_package)
        text += '\n'

    # if there are some package directories, add a TOC for theses subpackages
    if subs:
        text += format_heading(2, 'Subpackages')
        text += '.. toctree::\n\n'
        for sub in subs:
            text += '    %s.%s\n' % (makename(master_package, subroot), sub)
        text += '\n'

    if submods:
        text += format_heading(2, 'Submodules')
        if opts.separatemodules:
            text += '.. toctree::\n\n'
            for submod in submods:
                modfile = makename(master_package, makename(subroot, submod))
                text += '   %s\n' % modfile

                # generate separate file for this module
                if not opts.noheadings:
                    filetext = format_heading(1, '%s module' % modfile)
                else:
                    filetext = ''
                filetext += format_directive(makename(subroot, submod),
                                             master_package)
                write_file(modfile, filetext, opts)
        else:
            for submod in submods:
                modfile = makename(master_package, makename(subroot, submod))
                if not opts.noheadings:
                    text += format_heading(2, '%s module' % modfile)
                text += format_directive(makename(subroot, submod),
                                         master_package)
                text += '\n'
        text += '\n'

    if not opts.modulefirst:
        text += format_heading(2, 'Module contents')
        text += format_directive(subroot, master_package)

    write_file(makename(master_package, subroot), text, opts)


def create_modules_toc_file(modules, opts, name='modules'):
    """Create the module's index."""
    text = format_heading(1, '%s' % opts.header)
    text += '.. toctree::\n'
    text += '   :maxdepth: %s\n\n' % opts.maxdepth

    modules.sort()
    prev_module = ''
    for module in modules:
        # look if the module is a subpackage and, if yes, ignore it
        if module.startswith(prev_module + '.'):
            continue
        prev_module = module
        text += '   %s\n' % module

    write_file(name, text, opts)


def walk_dir_tree(rootpath, excludes, opts):
    """
    Look for every file in the directory tree and create the corresponding
    ReST files.
    """
    # FIXME Remove print() when done
    print('Started', file=sys.stderr)
    toplevels = []
    if has_initpy(rootpath):
        root_package = rootpath.split(os.sep)[-1]
    else:
        # Generate .rst files for the top level modules even if we are  
        # not in a package (this is a one time exception)
        root_package = None
        mods = get_modules(os.listdir(rootpath), excludes, opts, rootpath)
        for module in mods:
            create_module_file(root_package, module, opts)
            toplevels.append(module)
    # Do the actual directory tree walk
    for pkgname,mods,subpkgs in pkgname_modules_subpkgs(rootpath,excludes,opts):
        create_package_file(root_package, pkgname, mods, opts, subpkgs)
        toplevels.append(makename(root_package, pkgname))

    return toplevels


def has_initpy(directory):
    return os.path.isfile( join(directory, INITPY) )


def pkgname_modules_subpkgs(rootpath, excluded, opts):
    """A generator that filters out the packages and modules as desired and 
    yields tuples of (package name, modules, subpackages).  
    """
    for root, dirs, files in walk(rootpath, followlinks=opts.followlinks):
        if root in excluded:
            del dirs[:] # skip all subdirectories as well
            continue
        if INITPY not in files:
            if root != rootpath:
                del dirs[:]
            continue
        pkg_name = root[len(rootpath):].lstrip(os.sep).replace(os.sep, '.')
        if not opts.includeprivate and pkg_name.startswith('_'):
            del dirs[:]
            continue
        modules = get_modules(files, excluded, opts, root)
        subpkgs = get_subpkgs(dirs,  excluded, opts, root, rootpath)
        dirs[:] = subpkgs # visit only subpackages
        has_sg_to_doc = True 
        if opts.respect_all:
            all_attr, has_docstr = get_all_attr_has_docstr(rootpath, root)
            has_sg_to_doc = has_docstr or bool(all_attr)
            # has_sg_to_doc: e.g. multiprocessing.dummy has nonempty __all__ but 
            # no modules, subpkgs or docstring to document -> still document it!                   
            modules = get_only_modules(all_attr, modules)
        if modules or subpkgs or has_sg_to_doc:
                yield pkg_name, modules, subpkgs


def get_modules(files, excluded, opts, root):
    """Filter out and sort the considered python modules from files."""
    return sorted( os.path.splitext(f)[0] for f in files
                   if os.path.splitext(f)[1] in PY_SUFFIXES and
                      norm_path(root, f) not in excluded    and
                      f != INITPY                           and
                     (not f.startswith('_') or opts.includeprivate) )


def get_subpkgs(dirs, excluded, opts, root, rootpath):
    """Filter out and sort the considered subpackages from dirs."""    
    exclude_prefixes = ('.',) if opts.includeprivate else ('.', '_')
    return sorted( d for d in dirs 
                      if not d.startswith(exclude_prefixes) and
                         norm_path(root, d) not in excluded and
                         has_initpy( join(root, d) )        and 
                         pkg_to_doc(opts, root, d, rootpath)    )


def pkg_to_doc(opts, root, d, rootpath):
    if not opts.respect_all:
        return True
    all_attr, has_docstr = get_all_attr_has_docstr(rootpath, join(root, d))
    return all_attr is None or bool(all_attr) or has_docstr 


def get_only_modules(all_attr, modules):
    """If ``__all__`` is not present in ``__init__.py``, we take all the modules
    in the current directory. Otherwise, we only keep those element of 
    ``__all__`` that are also modules in the current directory."""
    if all_attr is None:
        return modules
    mods = set(modules)
    return [m for m in all_attr if m in mods]


# TODO Update doc
def get_all_attr_has_docstr(rootpath, path, cached={}):
    """Returns a tuple: the ``__all__`` attribute of the package as a list 
    (``None`` if ``__all__`` is not  present) and a ``bool`` indicating whether
    the module has a doc string. Calls ``sys.exit`` on failure 
    (e.g. ``ImportError``).
    """
    # FIXME Why does caching break scipy.linalg?
    #if path in cached:
    #    return cached[path]
    
    try:
        path_before = list(sys.path)
        modules_before = set(sys.modules)
        head, pkg = find_top_package(rootpath, path)
        sys.path = sys.path + [head]  # FIXME Prepend or append? No difference on /usr/lib/python2.7
        module = importlib.import_module(pkg)
        all_attrib = getall_from(module)
        # cairo and zope has __doc__ but it is None
        has_docstring = getattr(module, '__doc__', None) is not None
        cached[path] = (all_attrib, has_docstring)
        return all_attrib, has_docstring
    except:
        print('\n', tb.format_exc()[:-1], file=sys.stderr)         
        print('Please make sure that', pkg, 'can be imported',
              '(or exclude %s).' % path, file=sys.stderr)
#       sys.exit(1)        # FIXME Or a --forgiving option?
    finally:
        difference = sys.modules.viewkeys() - modules_before        
        for k in difference:
            sys.modules.pop(k)
        sys.path = path_before
# TODO Use __import__? I don't see any benefit in using the importlib here.
#      But it does break Python 2.6 compatibility...
#      Try caching path and associated __all__, we currently look at each 
#      package twice anyway    


def find_top_package(root, path):
    """Walks up in the directory hierarchy to find the top level package or 
    until hitting the root. For example:
        root  = '/usr/lib/python2.7'
        path  = '/usr/lib/python2.7/dist-packages/scipy/sparse/linalg/isolve'    
        result: '/usr/lib/python2.7/dist-packages'  'scipy.sparse.linalg.isolve'
    """
    assert path.startswith(root), '\n%s\n%s' % (root, path)
    assert has_initpy(path), path
    roothead = os.path.dirname(root)
    head, tail = os.path.split(path)
    while roothead != head and has_initpy(head): 
        head, pkg = os.path.split(head)
        tail = join(pkg, tail)
    return head, string.replace(tail, os.sep, '.')


def getall_from(module):
    all_attr = getattr(module, '__all__', None)
    # Some packages (for example dbus.mainloop.__init__.py) uses a tuple.
    # Convert __all__ to list if necessary. 
    if all_attr is not None and not isinstance(all_attr, list):
        all_attr = list(all_attr) 
    return all_attr


def norm_path(root, mod_or_dir):
    return os.path.normpath( join(root, mod_or_dir) )


def main(argv=sys.argv):
    """Parse and check the command line arguments."""
    parser = optparse.OptionParser(
        usage="""\
usage: %prog [options] -o <output_path> <module_path> [exclude_path, ...]

Look recursively in <module_path> for Python modules and packages and create
one reST file with automodule directives per package in the <output_path>.

The <exclude_path>s can be files and/or directories that will be excluded
from generation.

Note: By default this script will not overwrite already created files.""")

    parser.add_option('-o', '--output-dir', action='store', dest='destdir',
                      help='Directory to place all output', default='')
    parser.add_option('-d', '--maxdepth', action='store', dest='maxdepth',
                      help='Maximum depth of submodules to show in the TOC '
                      '(default: 4)', type='int', default=4)
    parser.add_option('-f', '--force', action='store_true', dest='force',
                      help='Overwrite existing files')
    parser.add_option('-l', '--follow-links', action='store_true',
                      dest='followlinks', default=False,
                      help='Follow symbolic links. Powerful when combined '
                      'with collective.recipe.omelette.')
    parser.add_option('-n', '--dry-run', action='store_true', dest='dryrun',
                      help='Run the script without creating files')
    parser.add_option('-e', '--separate', action='store_true',
                      dest='separatemodules',
                      help='Put documentation for each module on its own page')
    parser.add_option('-P', '--private', action='store_true',
                      dest='includeprivate',
                      help='Include "_private" modules')
    parser.add_option('-T', '--no-toc', action='store_true', dest='notoc',
                      help='Don\'t create a table of contents file')
    parser.add_option('-E', '--no-headings', action='store_true',
                      dest='noheadings',
                      help='Don\'t create headings for the module/package '
                           'packages (e.g. when the docstrings already contain '
                           'them)')
    parser.add_option('-M', '--module-first', action='store_true',
                      dest='modulefirst',
                      help='Put module documentation before submodule '
                      'documentation')
    parser.add_option('-s', '--suffix', action='store', dest='suffix',
                      help='file suffix (default: rst)', default='rst')
    parser.add_option('-F', '--full', action='store_true', dest='full',
                      help='Generate a full project with sphinx-quickstart')
    parser.add_option('-H', '--doc-project', action='store', dest='header',
                      help='Project name (default: root module name)')
    parser.add_option('-A', '--doc-author', action='store', dest='author',
                      type='str',
                      help='Project author(s), used when --full is given')
    parser.add_option('-V', '--doc-version', action='store', dest='version',
                      help='Project version, used when --full is given')
    parser.add_option('-R', '--doc-release', action='store', dest='release',
                      help='Project release, used when --full is given, '
                      'defaults to --doc-version')
    parser.add_option('--version', action='store_true', dest='show_version',
                      help='Show version information and exit')
    parser.add_option('--respect-all', action='store_true',
                      dest='respect_all',
                      help='Respect __all__ when looking for modules')    

    (opts, args) = parser.parse_args(argv[1:])

    if opts.show_version:
        print('Sphinx (sphinx-apidoc) %s' %  __version__)
        return 0

    if not args:
        parser.error('A package path is required.')

    rootpath, excludes = args[0], args[1:]
    if not opts.destdir:
        parser.error('An output directory is required.')
    if opts.header is None:
        opts.header = os.path.normpath(rootpath).split(os.sep)[-1]
    if opts.suffix.startswith('.'):
        opts.suffix = opts.suffix[1:]
    if not os.path.isdir(rootpath):
        print('%s is not a directory.' % rootpath, file=sys.stderr)
        sys.exit(1)
    if opts.includeprivate and opts.respect_all:
        msg = 'Either --private or --respect-all but not both'
        print(msg, file=sys.stderr)
        sys.exit(1)        
    if not os.path.isdir(opts.destdir):
        if not opts.dryrun:
            os.makedirs(opts.destdir)
    rootpath =   os.path.normpath(os.path.abspath(rootpath))
    excludes = { os.path.normpath(os.path.abspath(excl)) for excl in excludes }
    modules = walk_dir_tree(rootpath, excludes, opts)
    if opts.full:
        modules.sort()
        prev_module = ''
        text = ''
        for module in modules:
            if module.startswith(prev_module + '.'):
                continue
            prev_module = module
            text += '   %s\n' % module
        d = dict(
            path = opts.destdir,
            sep  = False,
            dot  = '_',
            project = opts.header,
            author = opts.author or 'Author',
            version = opts.version or '',
            release = opts.release or opts.version or '',
            suffix = '.' + opts.suffix,
            master = 'index',
            epub = True,
            ext_autodoc = True,
            ext_viewcode = True,
            makefile = True,
            batchfile = True,
            mastertocmaxdepth = opts.maxdepth,
            mastertoctree = text,
        )
        if not opts.dryrun:
            from sphinx import quickstart as qs
            qs.generate(d, silent=True, overwrite=opts.force)
    elif not opts.notoc:
        create_modules_toc_file(modules, opts)

if __name__ == '__main__':
    main()
