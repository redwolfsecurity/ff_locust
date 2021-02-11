# FF Locust

[![Build Status](https://jenkins.development.redwolfsecurity.com/buildStatus/icon?job=RedWolfSecurity%2Fff_locust%2Fmaster)](https://jenkins.development.redwolfsecurity.com/me/my-views/view/all/job/RedWolfSecurity/job/ff_locust/job/master/)

# Features!

  - Generate FF metrics from running locust scripts 
  - Integrate RedWolf table server API in Python code

### Requirements

- Runs on Python 3.8
- Requires `requests` library

### Importing
```py
# At top of 
from ff_locust import FF_Locust
fancy_locust = FF_Locust()
```

### Usage
```py
# Parameters:
# table   - If a RedWolf portal url is found in the environment the corresponding list server is used
#           If not, a local file is searched for. REQUIRED.
# looping - The default is True. Set to false to return None when end of tsv is reached.
#
# Errors:
# Current implementation logs errors with 'FF_LOG' prepended.
# In the case of an error the return is False.
json = fancy_locust.get_data_next(table = 'users.tsv', looping = True)

# The above will output JSON like:
# {
#    '__list': 'users',
#    '__timestamp_epoch_ms': 1613070277418,
#    '__index': 0,
#    '__remaining_count': 1,
#    '__list_count': 1,
#    'first_name': 'John',
#    'last_name': 'Doe'
# }
# Where first_name and last_name are column headers in the provided users.tsv file.
# These parameters are accessible VIA:
first_name = json['first_name']
last_name = json['last_name']
```
