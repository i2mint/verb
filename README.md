# verb
Easy make mini-languages to do python things.


To install:	```pip install verb```



# A quick intro to Command


```python
from pprint import pprint
from functools import partial
import json
import operator as o
from verb import *
from lined import Pipe  # lined is installed with verb

print_jdict = Pipe(partial(json.dumps, indent=2), print)
```


```python
# In a nutshell, you make a str-to-func mapping (or use the default)

func_of_op_str = {  # Note: Order represents precedence!
    '-': o.sub,
    '+': o.add,
    '*': o.mul,
    '/': o.truediv,
}

# You give it a command string

command_str = '1 + 2 - 3 * 4 / 5'
command = Command(command_str, func_of_op_str)

# You execute the command
command()
```




    0.5999999999999996



It may be useful to see what the operation structure looks like


```python
d = command.to_dict()
d
```




    {'-': ({'+': (1, 2)}, {'*': (3, {'/': (4, 5)})})}




```python
# Or if you read better with indents
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
                5
              ]
            }
          ]
        }
      ]
    }


That same dict can be used as a parameter to make the same command


```python
command = Command(d, func_of_op_str)
command()
```




    0.5999999999999996



## Example: Table Selector Mini Language


```python
import operator as o
from typing import Callable, Mapping
from functools import partial

import pandas as pd
from lined import Pipe
from verb import str_to_basic_pyobj, Command


dflt_func_of_op_str_for_table_selection = {  # Note: Order represents precedence!
    '&': o.__and__,
    '==': o.__eq__,
    '<=': o.__le__,
    '>=': o.__ge__,
    '<': o.__lt__,
    '>': o.__gt__,
}


def mk_table_selector(
    table: pd.DataFrame,
    func_of_op_str: Mapping[str, Callable] = dflt_func_of_op_str_for_table_selection
):

    def leaf_processor(x):
        x = str_to_basic_pyobj(x)
        if x in df:
            return df[x]
        return x

    run_command = Pipe(
        partial(
            Command.from_string,
            func_of_op_str=func_of_op_str,
            leaf_processor=leaf_processor
        ),
        lambda f: f(),
        lambda idx: df[idx],
    )

    return run_command
```


```python
import pandas as pd

# from mongodol.tests import data
# data.nums_and_lans

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
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
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
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
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
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
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
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
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
