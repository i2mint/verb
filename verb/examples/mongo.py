from typing import Optional
from verb import Command
import operator as o

dflt_func_of_op_str_for_table_selection = {
    "|": o.__or__,
    "&": o.__and__,
    "==": o.__eq__,
    "<=": o.__le__,
    ">=": o.__ge__,
    "<": o.__lt__,
    ">": o.__gt__,
}

DFLT_OP_TRANSLATION = {
    "&": "$and",
    "|": "$or",
    "<=": "$lte",
    ">=": "$gte",
    "<": "$lt",
    ">": "$gt",
}


def post_process_dict(d, op_translation=DFLT_OP_TRANSLATION):
    """
    Process a dict of key, values of the form key, tuple"""
    result = []
    for k, v in d.items():
        if k == "==":
            result.append((v[0], v[1]))
        else:
            result.append((v[0], {op_translation[k]: v[1]}))
    return dict(result)


def post_process_and_expression(expr_dict, op_translation=DFLT_OP_TRANSLATION):
    result = []
    processor = lambda x: list(map(post_process_dict, x))
    for k, v in expr_dict.items():

        if k in "&|":
            result.append((op_translation[k], processor(v)))

    return dict(result)


class CommandMongo(Command):
    """
    Class to convert string commands to mongodb query syntax

    Usage:
    >>> command_str = "session == 1 & rpm>=500 & phase == 0"
    >>> command = CommandMongo(command_str, dflt_func_of_op_str_for_table_selection)
    >>> command.to_dict()
    {'$and': [{'session': 1}, {'rpm': {'$gte': 500}}, {'phase': 0}]}

    """

    def to_dict(self, op_str_of_func: Optional[dict] = None):
        res = super().to_dict(op_str_of_func)
        return post_process_and_expression(res, op_translation=DFLT_OP_TRANSLATION)

