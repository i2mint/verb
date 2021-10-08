"""This module demos how to interpret a different minilanguage by translating it
to the verb framework"""

from verb import Command, Literal
from inspect import signature


def mk_minilanger():
    def command_dict(input_val, spec: dict):
        operator, tag, value = spec['operator'], spec['tag'], spec['value']
        if not isinstance(input_val, Literal):
            input_val = Literal(input_val)
        return {operator: ({'[]': (input_val, tag)}, value)}

    def command(command_dict, interpreter_dict):
        return Command.from_dict(command_dict, interpreter_dict)

    def result(command):
        return command()

    from meshed import DAG

    minilanger = DAG([result, command_dict, command])
    return minilanger


def test_minilanger():
    minilanger = mk_minilanger()
    assert str(signature(minilanger)) == '(input_val, spec: dict, interpreter_dict)'
    minilanger.dot_digraph()

    import operator as o
    from functools import partial

    func_of_key = {
        '>': o.gt,
        '<': o.lt,
        '>=': o.ge,
        '<=': o.le,
        '==': o.eq,
        '[]': lambda d, tag: d[tag]
        # 'call': lambda f, x: f(x)
    }

    minilang = partial(minilanger, interpreter_dict=func_of_key)

    func1 = partial(minilang, spec={'tag': 'temperature', 'operator': '<', 'value': 0})
    assert not func1({'temperature': 2})
    assert func1({'temperature': -3})
    assert func1({'temperature': -10, 'rpm': 234})

    func2 = partial(
        minilang, spec={'tag': 'machine', 'operator': '==', 'value': 'fridge'}
    )
    assert func2({'machine': 'fridge'})
    assert not func2({'machine': 'coffee maker'})
    assert func2({'temperature': -10, 'machine': 'fridge', 'color': 'blue'})

