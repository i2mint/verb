"""Misc tests"""

from verb import Command


def random_doctest():
    """
    Note that Literal is/may be needed to avoid Command to interpret 'temperature' as an operator

    >>> from verb import Command, Literal
    >>> import operator as o
    >>> condition_1 = {'<': ({'[]': (Literal({'temperature': 2}), 'temperature')}, 80)}
    >>> condition_2 = {'>': ({'[]': (Literal({'temperature': 2}), 'temperature')}, 60)}
    >>> cond_1_and_2 = {'&': (condition_1, condition_2)}
    >>> func_of_key = {'&': o.and_, '>': o.gt, '<': o.lt, '[]': lambda d, tag: d[tag]}
    >>> Command.from_dict(cond_1_and_2, func_of_key)()
    False

    We can change the meaning of the operator, below a non-sensical one which results
    in True

    >>> func_of_key = {'&': o.and_, '>': o.gt, '<': o.lt, '[]': lambda d, tag: 70}
    >>> Command.from_dict(cond_1_and_2, func_of_key)()
    True
    """
