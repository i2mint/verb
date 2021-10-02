# verb
Easy make mini-languages to do python things.

To install:	```pip install verb```

Do things like this:

```python
from verb import mk_executer

func_of_key = {
    'plus': lambda x, y: x + y,
    'minus': lambda x, y: x - y,
}
execute = mk_executer(func_of_key)
execute('3 minus 2 plus 1')
## 2
execute('9 minus 6')
## 3

```

# A quick intro to Command

Uses cases: In situations where you want to get some input from a user (from the web,
in a command line, etc.) that specifies a computation to be carried out, you know
(right) that you definitely shouldn't resort to using `eval` or `exec`.
Because it's dangerous for everyone involved -- let's just not go there.

`verb` offers an alternative: Easily building minilanguages that will allow the user
to only execute the functions you choose, through a vocabulary you choose,
and everyone can go home (as) safe (as you allow).

In a nutshell, you make a key-to-func mapping (or use the default). 
This `func_of_key` mapping is what specifies your _interpreter_:

```python
from verb import *
import operator as o

func_of_key = {  # Note: Order represents precedence!
    '-': o.sub,
    '+': o.add,
    '*': o.mul,
    '/': o.truediv,
}
```

Now you have a minilanguage! Out-of-the-box it will allow you to "speak it in string"
or "speak it in json/dict", but you can extend to enable the language to be written in
any container you want.

If you give it a "command string":


```python
command_str = '1 + 2 - 3 * 4 / 8'
command = Command(command_str, func_of_key)
```

>>> command_str = '1 + 2 - 3 * 4 / 8'
>>> command = Command(command_str, func_of_key)

It will use `func_of_key` to both parse it and replace the keys with an indication
that the corresponding function should be called.
`command` is a callable object, and when you call it, 
it executes it's instructions:


```python
command()
```


    1.5


It may be useful to see what the operation structure looks like


```python
d = command.to_dict()
d
```


    {'-': ({'+': (1, 2)}, {'*': (3, {'/': (4, 8)})})}




```python
# Or if you read better with indents

from functools import partial
import json
from lined import Pipe

print_jdict = Pipe(partial(json.dumps, indent=2), print)  # Note: Only works if your dict is JSON-izable. 

print_jdict(d)
```

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


```python
command = Command(d, func_of_key)
command()
```



    1.5



## Example: Table Selector Mini Language


```python
import operator as o
from typing import Callable, Mapping
from functools import partial

import pandas as pd
from lined import Pipe
from verb import str_to_basic_pyobj, Command


dflt_func_of_key_for_table_selection = {  # Note: Order represents precedence!
    '&': o.__and__,
    '==': o.__eq__,
    '<=': o.__le__,
    '>=': o.__ge__,
    '<': o.__lt__,
    '>': o.__gt__,
}


def mk_table_selector(
    table: pd.DataFrame,
    func_of_key: Mapping[str, Callable] = dflt_func_of_key_for_table_selection
):

    def leaf_processor(x):
        x = str_to_basic_pyobj(x)
        if x in table:
            return table[x]
        return x

    run_command = Pipe(
        partial(
            Command.from_string,
            func_of_key=func_of_key,
            leaf_processor=leaf_processor
        ),
        lambda f: f(),
        lambda idx: table[idx],
    )

    return run_command
```


```python
import pandas as pd

df = pd.DataFrame(
    [{'source': 'audio', 'bt': 5, 'tt': 7, 'annot': 'cat'},
     {'source': 'audio',
        'bt': 6,
        'tt': 9,
        'annot': 'dog',
        'comments': 'barks and chases cat away'},
        {'source': 'visual', 'bt': 5, 'tt': 8, 'annot': 'cat'},
        {'source': 'visual',
         'bt': 6,
         'tt': 15,
         'annot': 'dog',
         'comments': 'dog remains in view after bark ceases'}]
)
df
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>source</th>
      <th>bt</th>
      <th>tt</th>
      <th>annot</th>
      <th>comments</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>audio</td>
      <td>5</td>
      <td>7</td>
      <td>cat</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>audio</td>
      <td>6</td>
      <td>9</td>
      <td>dog</td>
      <td>barks and chases cat away</td>
    </tr>
    <tr>
      <th>2</th>
      <td>visual</td>
      <td>5</td>
      <td>8</td>
      <td>cat</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>3</th>
      <td>visual</td>
      <td>6</td>
      <td>15</td>
      <td>dog</td>
      <td>dog remains in view after bark ceases</td>
    </tr>
  </tbody>
</table>
</div>




```python
run_command = mk_table_selector(df)
```


```python
run_command('source == audio')
```




<div>

<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>source</th>
      <th>bt</th>
      <th>tt</th>
      <th>annot</th>
      <th>comments</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>audio</td>
      <td>5</td>
      <td>7</td>
      <td>cat</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>1</th>
      <td>audio</td>
      <td>6</td>
      <td>9</td>
      <td>dog</td>
      <td>barks and chases cat away</td>
    </tr>
  </tbody>
</table>
</div>




```python
run_command('tt <= 8')
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>source</th>
      <th>bt</th>
      <th>tt</th>
      <th>annot</th>
      <th>comments</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>audio</td>
      <td>5</td>
      <td>7</td>
      <td>cat</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>2</th>
      <td>visual</td>
      <td>5</td>
      <td>8</td>
      <td>cat</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>




```python
run_command('source == audio & tt <= 8')
```




<div>
<table border="1" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>source</th>
      <th>bt</th>
      <th>tt</th>
      <th>annot</th>
      <th>comments</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>audio</td>
      <td>5</td>
      <td>7</td>
      <td>cat</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>
