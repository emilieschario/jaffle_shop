/*
  This snapshot table will live in:
    analytics.snapshots.orders_snapshot
  Run with below command:
    dbt snapshot
*/


{% snapshot orders_snapshot %}

    {{
        config
(
          target_database='wam-bam-258119',
          target_schema='dbt_bq_example',
          unique_key='user_id',
          
          strategy='check',
          check_cols=['status'],
        )
    }}

-- Pro-Tip: Use sources in snapshots!
select * from {{ ref('raw_orders') }}
    
{% endsnapshot %}