{{
  config(
    materialized = "udf",
    arguments = {"json_field": "varchar(2000)", "json_expected_keys": "varchar(2000)"},
    return_type = "integer", 
    language = "plpythonu"
  )
}}

import json
provided_keys = set(json.loads(json_field).keys())
expected_keys = set(json.loads(json_expected_keys))
return len(provided_keys - expected_keys)
