'''
Created on 11 May 2018

@author: David

Roadmap:
    - Define a better unit test object containing various data types like
    various datetime formats, int, float, exp, ccy, url/email etc. 
    - Add support for data type tests. The report should make it clear
    which data type tests succeeded for a given field in the document set.
'''


def _profile_field(parent, fieldlist, inxfield=0):
    assert len(fieldlist) > 0 and inxfield >= 0

    parent.stats.counter += 1

    if (inxfield >= len(fieldlist) - 1):
        return

    if not hasattr(parent, 'children'):
        setattr(parent, 'children', _FieldNode())

    try:
        child = getattr(parent.children, fieldlist[inxfield])
    except:
        child = _FieldNode()
        setattr(parent.children, fieldlist[inxfield], child)
    finally:
        _profile_field(child, fieldlist, inxfield + 1)


def _printFieldNode(node, name, logger, level=0):
    if hasattr(node, 'stats'):
        for attr in dir(node.stats):
            if(attr[0] != '_' and not callable(attr)):
                outstr = f'{name} - {attr}: {getattr(node.stats, attr)}'
                outstr = outstr.rjust(len(outstr) + 4 * level)
                if (logger):
                    logger.info(outstr)
                else:
                    print(outstr)
    if hasattr(node, 'children'):
        for attr in dir(node.children):
            if(attr[0] != '_' and not callable(attr)):
                _printFieldNode(getattr(node.children, attr),
                                name + '.' + attr, logger, level + 1)


def _fieldspec_generator(indict, pre=None):
    pre = pre[:] if pre else []
    if isinstance(indict, dict):
        for key, value in indict.items():
            if isinstance(value, dict):
                for d in _fieldspec_generator(value, pre + [key]):
                    yield d
            elif isinstance(value, list) or isinstance(value, tuple):
                for v in value:
                    for d in _fieldspec_generator(v, pre + [key]):
                        yield d
            else:
                yield pre + [key, value]
    else:
        yield indict


class _FieldStats:
    def __init__(self):
        self.counter = 0


class _FieldNode:
    def __init__(self):
        self.stats = _FieldStats()


class Profiler:
    def __init__(self):
        self.root_node = _FieldNode()

    def update(self, obj):
        fsg = _fieldspec_generator(obj)
        for fieldspec in fsg:
            #             print(fieldspec)
            _profile_field(self.root_node, fieldspec)

    def print(self, root_node_alias='<Root>', logger=None):
        _printFieldNode(self.root_node, root_node_alias, logger)


if __name__ == '__main__':
    testobj = {u'body': [{u'declarations': [{u'id': {u'name': u'i',
                                                     u'type': u'Identifier'},
                                             u'init': {u'type': u'Literal', u'value': 2},
                                             u'type': u'VariableDeclarator'}],
                          u'kind': u'var',
                          u'type': u'VariableDeclaration'},
                         {u'declarations': [{u'id': {u'name': u'j',
                                                     u'type': u'Identifier'},
                                             u'init': {u'type': u'Literal', u'value': 4},
                                             u'type': u'VariableDeclarator'}],
                          u'kind': u'var',
                          u'type': u'VariableDeclaration'},
                         {u'declarations': [{u'id': {u'name': u'answer',
                                                     u'type': u'Identifier'},
                                             u'init': {u'left': {u'name': u'i',
                                                                 u'type': u'Identifier'},
                                                       u'operator': u'*',
                                                       u'right': {u'name': u'j',
                                                                  u'type': u'Identifier'},
                                                       u'type': u'BinaryExpression'},
                                             u'type': u'VariableDeclarator'}],
                          u'kind': u'var',
                          u'type': u'VariableDeclaration'}],
               u'type': u'Program'}

    p = Profiler()
    p.update(testobj)
    p.print()
