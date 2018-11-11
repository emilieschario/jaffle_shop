select
*,
{{ref('f_count_keys')}}(my_json_column, '["a"]')
-- {{ref('f_count_keys')}}(my_json_column)
from {{ref('raw_data_with_json')}}