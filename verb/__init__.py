"""
Tools to make mini-languages

>>> import operator as o
>>> from verb import *

In a nutshell, you make a str-to-func mapping (or use the default)

>>> func_of_op_str = {  # Note: Order represents precedence!
...     '-': o.sub,
...     '+': o.add,
...     '*': o.mul,
...     '/': o.truediv,
... }


You give it a command string

>>> command_str = '1 + 2 - 3 * 4 / 8'
>>> command = Command(command_str, func_of_op_str)

You execute the command

>>> command()
1.5

It may be useful to see what the operation structure looks like

>>> d = command.to_dict()
>>> d
{'-': ({'+': (1, 2)}, {'*': (3, {'/': (4, 8)})})}

Or if you read better with indents

>>> from lined import Pipe; import json; from functools import partial
>>> print_jdict = Pipe(partial(json.dumps, indent=2), print)
>>> print_jdict(d)
{
  "-": [
    {
      "+": [
        1,
        2
      ]
    },
    {
      "*": [
        3,
        {
          "/": [
            4,
            8
          ]
        }
      ]
    }
  ]
}

That same dict can be used as a parameter to make the same command

>>> command = Command(d, func_of_op_str)
>>> command()
1.5


"""

from functools import partial, reduce, wraps
from dataclasses import dataclass
from typing import Callable, Iterable, Optional, Union, Any
import operator as o

from lined import Pipe as P, iterize as I
from lined.tools import expanded_args

PI = P(P, I)  # you like? Well, too bad! I think it's cute and useful!

no_default = type('no_default', (), {})()


def transform_if_possible(
    x: Any,
    funcs: Iterable[Callable],
    pass_on_exceptions: Union[
        BaseException, Iterable[BaseException]
    ] = Exception,
):
    """Will try to apply the functions of funcs one by one, returning the value if no errors occur,
    returning x as is if none of the functions  work
    """
    for func in funcs:
        try:
            return func(x)
        except pass_on_exceptions:
            pass
    return x


str_to_basic_pyobj = partial(
    transform_if_possible,
    funcs=[
        int,
        float,
        {'True': True, 'False': False, 'None': None}.__getitem__,
    ],
)
str_to_basic_pyobj.__doc__ = "Casts to int or float if possible, True or False or None if the (string) 'True' or 'False', if not, explodes"
assert list(
    map(str_to_basic_pyobj, ['3.14', '3', 'True', 'False', 'something else'])
) == [3.14, 3, True, False, 'something else']

dflt_leaf_processor = P(str.strip, str_to_basic_pyobj)


def name_func(func, name, name_attr='_name'):
    def _func(*args, **kwargs):
        return func(*args, **kwargs)

    setattr(_func, name_attr, name)
    return _func


def add_key_as_func_attr(d: dict, name_attr='_name') -> dict:
    return {k: name_func(v, k, name_attr) for k, v in d.items()}


def mk_op_applicable_to_multiple_args(op_func):
    """Make a binary function op_func(a,b) work on with unbounded args (op_func(a,b,c,d...))

    >>> sum_multiple = mk_op_applicable_to_multiple_args(lambda a, b: a + b)
    >>> sum_multiple(1)
    1
    >>> sum_multiple(1,2)
    3
    >>> sum_multiple(1,2,3,4)
    10
    >>> sum_multiple(*range(7))
    21
    """
    return expanded_args(partial(reduce, op_func))


dflt_func_of_op_str = {  # Note: Order represents precedence!
    # an and function that will work with multiple inputs, not just two (and(x,y,z,...))
    '&': mk_op_applicable_to_multiple_args(o.and_),
    '|': mk_op_applicable_to_multiple_args(o.or_),
    '==': o.eq,
    '!=': o.ne,
    '<=': o.le,
    '>=': o.ge,
    '<': o.lt,
    '>': o.gt,
    '-': o.sub,
    '+': o.add,
    '*': o.mul,
    '/': o.truediv,
}

dflt_func_of_op_str = add_key_as_func_attr(dflt_func_of_op_str)


def reverse_dict(d: dict):
    return {v: k for k, v in d.items()}


def identity(x):
    return x


@dataclass(init=False, unsafe_hash=True)
class Command:
    func: Callable = identity
    args: Iterable = ()
    _func_of_op_str = None

    def __init__(self, func, *args):
        if isinstance(func, (dict, str)):
            func_of_op_str = next(iter(args), dflt_func_of_op_str)
            self._func_of_op_str = func_of_op_str
            if isinstance(func, dict):
                command = Command.from_dict(func, func_of_op_str)
            elif isinstance(func, str):
                command = Command.from_string(func, func_of_op_str)
            func, args = command.func, command.args
        self.func = func
        self.args = args

    def __call__(self):
        return self.func(*self.arg_execution_gen())

    def arg_execution_gen(self):
        for arg in self.args:
            if isinstance(arg, Command):
                yield arg()
            else:
                yield arg

    def to_dict(self, op_str_of_func: Optional[dict] = None):
        if op_str_of_func is None and self._func_of_op_str:
            op_str_of_func = reverse_dict(self._func_of_op_str)
        func = self.func
        if func in (op_str_of_func or {}):
            func = op_str_of_func[self.func]

        def process_args():
            for arg in self.args:
                if isinstance(arg, Command):
                    if arg.func == identity:
                        yield arg.args[0]
                    else:
                        yield arg.to_dict(op_str_of_func)
                else:
                    yield arg

        return {func: tuple(process_args())}

    @classmethod
    def from_dict(cls, d: dict, func_of_key: Optional[dict] = None):
        """Make a command from a dict specification
        If func_of_key is not given, the keys

        >>> assert Command.parse_to_dict(
        ...     'machine == crane & rpm >= 3 & pressure < 21.2', dflt_func_of_op_str) == (
        ...    {'&': [{'==': ['machine', 'crane']},
        ...           {'>=': ['rpm', 3]},
        ...           {'<': ['pressure', 21.2]}]}
        ... )

        """
        assert len(d) == 1
        func, args = next(iter(d.items()))
        if func_of_key is not None:
            func = func_of_key.get(func, func)
        assert isinstance(func, Callable), (
            f'Your func must be callable. '
            f'Was {func}. Perhaps you meant to specify a func_of_key map from string to func?'
        )

        def gen():
            for arg in args:
                if isinstance(arg, dict) and len(arg) == 1:
                    yield Command.from_dict(arg, func_of_key)
                else:
                    yield Command(identity, arg)

        args = list(gen())
        return cls(func, *args)

    @classmethod
    def from_string(
        cls,
        string: str,
        func_of_op_str: Optional[dict] = None,
        str_preprocessor=str.strip,
        leaf_processor=str_to_basic_pyobj,
    ):
        string = str_preprocessor(string)
        parser = partial(
            Command.from_string,
            func_of_op_str=func_of_op_str,
            str_preprocessor=str_preprocessor,
            leaf_processor=leaf_processor,
        )
        func_of_op_str = func_of_op_str or dflt_func_of_op_str
        for sep, func in func_of_op_str.items():
            parts = list(filter(str_preprocessor, string.split(sep)))
            if len(parts) > 1:
                return Command(func_of_op_str[sep], *map(parser, parts))
        return Command(identity, leaf_processor(string))

    def __repr__(self):
        func_name = getattr(
            self.func, '_name', getattr(self.func, '__nane__', repr(self.func))
        )
        if isinstance(self.args, Iterable):
            args_str = ', '.join(map(repr, self.args))
        else:
            args_str = self.args
        return f'{{{func_name}: [{args_str}]}}'

    @staticmethod
    def parse_to_dict(
        string,
        func_of_op_str: Optional[dict] = None,
        str_preprocessor=str.strip,
        leaf_processor=str_to_basic_pyobj,
    ):
        func_of_op_str = func_of_op_str or dflt_func_of_op_str
        string = str_preprocessor(string)
        parser = partial(
            Command.parse_to_dict,
            func_of_op_str=func_of_op_str,
            str_preprocessor=str_preprocessor,
            leaf_processor=leaf_processor,
        )
        for sep, func in func_of_op_str.items():
            parts = list(filter(str_preprocessor, string.split(sep)))
            if len(parts) > 1:
                return {sep: list(map(parser, parts))}
        return leaf_processor(string)
