-- depends on {{ref('f_count_keys')}}
select
*,
{{target.schema}}.f_count_keys(my_json_column)
from {{ref('raw_data_with_json')}}