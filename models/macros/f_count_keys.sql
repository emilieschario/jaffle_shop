{{
  config(
    materialized = "udf",
    arguments = {"json_field": "varchar(2000)"},
    return_type = "integer", 
    language = "plpythonu"
  )
}}

import json
provided_keys = set(json.loads(json_field).keys())
return len(provided_keys)
