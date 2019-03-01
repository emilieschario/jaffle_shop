with source as (

    select * from raw_jaffle_shop.customers

),

renamed as (

    select
        id as customer_id,
        first_name,
        last_name,
        email

    from source

)

select * from renamed
