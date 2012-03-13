## Copyright 2011, IOActive, Inc. All rights reserved.
##
## AndBug is free software: you can redistribute it and/or modify it under 
## the terms of version 3 of the GNU Lesser General Public License as 
## published by the Free Software Foundation.
##
## AndBug is distributed in the hope that it will be useful, but WITHOUT ANY
## WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS 
## FOR A PARTICULAR PURPOSE.  See the GNU Lesser General Public License for 
## more details.
##
## You should have received a copy of the GNU Lesser General Public License
## along with AndBug.  If not, see <http://www.gnu.org/licenses/>.

'implementation of the "class-trace" command'

import andbug.command, andbug.screed, andbug.options
from Queue import Queue
import re

def report_hit(t):
    t = t[0]
    try:
        with andbug.screed.section("trace %s" % t):
            for f in t.frames:
                name = str(f.loc)
                if f.native:
                    name += ' <native>'
                with andbug.screed.item(name):
                    for k, v in f.values.items():
                        andbug.screed.item( "%s=%s" %(k, v))
    finally:
        t.resume()

def search_classes(ctxt, cpath):
    p = re.compile(cpath, re.IGNORECASE)
    all_classes = []

    for c in ctxt.sess.classes():
        n = c.jni
        if n.startswith('L') and n.endswith(';'):
            n = n[1:-1].replace('/', '.')
        else:
            continue
        if p.match(n):
            all_classes.append(c)
    return all_classes


@andbug.command.action('<class-path> [<regex>]=False', aliases=('ct', 'ctrace'))
def class_trace(ctxt, cpath, regex=False):
    'reports calls to dalvik methods associated with a class'
    if regex and regex.lower() == "true":
        matched_classes = search_classes(ctxt, cpath)
    else:
        matched_classes = [ctxt.sess.classes(andbug.options.parse_cpath(cpath))]

    cpath = andbug.options.parse_cpath(cpath)

    with andbug.screed.section('Setting Hooks'):
        for c in matched_classes:
            c.hookEntries(func = report_hit)
            andbug.screed.item('Hooked %s' % c)

    ctxt.block_exit()

