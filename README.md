## dbt models for `jaffle_shop`

`jaffle_shop` is a fictional ecommerce store. This dbt project transforms raw
data from an app database into a customers and orders model ready for analytics.

The raw data from the app consists of customers, orders, and payments, with the
following entity-relationship diagram:

![Jaffle Shop ERD](/etc/jaffle_shop_erd.png)

This [dbt](https://www.getdbt.com/) project has a split personality:

- **Tutorial**: The [tutorial](https://github.com/fishtown-analytics/jaffle_shop/tree/master)
  branch is a useful minimum viable dbt project to get new dbt users up and
  running with their first dbt project. It includes [seed](https://docs.getdbt.com/reference#seed)
  files with generated data so a user can run this project on their own warehouse.
- **Demo**: The [demo](https://github.com/fishtown-analytics/jaffle_shop/tree/demo/master)
  branch is used to illustrate how we (Fishtown Analytics) would structure a dbt
  project. The project assumes that your raw data is already in your warehouse,
  so therefore the repo cannot be run as a standalone project. The demo is more
  complex than the tutorial as it is structured in a way that can be extended for
  larger projects.

### Using this project as a tutorial

> Note: Likely use [Airflow's BashOperator](https://docs.getdbt.com/docs/running-dbt-in-production#section-using-airflow) for production deployments

To get up and running with this project:

1. Install dbt using [these instructions](https://docs.getdbt.com/docs/installation).

2. Clone this repository. If you need extra help, see [these instructions](https://docs.getdbt.com/docs/use-an-existing-project).

3. Change into the `dbt_bigquery_example` directory from the command line:

```cmd
> cd dbt_bigquery_example
```

4. Set up a profile called `jaffle_shop` to connect to a data warehouse by
   following [these instructions](https://docs.getdbt.com/docs/configure-your-profile).
   If you have access to a data warehouse, you can use those credentials – we
   recommend setting your [target schema](https://docs.getdbt.com/docs/configure-your-profile#section-populating-your-profile)
   to be a new schema (dbt will create the schema for you, as long as you have
   the right priviliges). If you don't have access to an existing data warehouse,
   you can also setup a local postgres database and connect to it in your profile.

5. Ensure your profile is setup correctly from the command line:

```cmd
rem set the profiles directory in an environment variable, so debug points to the right files
rem replace the below with your own repo directory
set DBT_PROFILES_DIR=C:\Users\sungwon.chung\Desktop\repos\dbt_bigquery_example

rem connect to GCP
gcloud auth application-default login --scopes=https://www.googleapis.com/auth/userinfo.email,https://www.googleapis.com/auth/cloud-platform,https://www.googleapis.com/auth/drive.readonly

> dbt debug
```

6. Load the CSVs with the demo data set. This materializes the CSVs as tables in
   your target schema. Note that a typical dbt project **does not require this
   step** since dbt assumes your raw data is already in your warehouse.

> Note: You'll likely use [sources](https://docs.getdbt.com/docs/using-sources#section-defining-sources) in your `schema.yml` files because dbt assumes data is already loaded into your warehouse

```cmd
rem see a full breakdown of how dbt is creating tables in bigquery based on the csv files in the data directory
> dbt seed --show
```

7. Run the models:

Based on files in this directory: [models](/models)

```cmd
rem creates tables/views based off the sql and yml files
> dbt run

rem example CLI commands for how to utilize tagged models
rem https://docs.getdbt.com/docs/tags#section-selecting-models-with-tags
rem Run all models tagged "staging"
> dbt run --model tag:staging

rem Run all models tagged "staging", except those that are tagged hourly
rem should give a warning that nothing will run
> dbt run --model tag:staging --exclude tag:hourly

rem Run all of the models downstream of a source
> dbt run --model source:dbt_bq_example+

rem Run all of the models downstream of a specific source table
rem nothing will happen because the DAGs are dependent on other upstream tables
> dbt run --model source:dbt_bq_example.raw_orders+
```

> **NOTE:** If this steps fails, it might be that you need to make small changes to the SQL in the models folder to adjust for the flavor of SQL of your target database. Definitely consider this if you are using a community-contributed adapter.

8. Test the output of the models:

runs through all the tests defined in these specific file: [models/core/schema.yml](/models/core/schema.yml), [models/staging/schema.yml](/models/staging/schema.yml)

> Note: follow this [git guide](https://github.com/fishtown-analytics/corp/blob/master/git-guide.md) for merge requests

```cmd
rem runs through all the tests defined in the above file by
rem generating SQL for out of the box functionality such as not_null and unique fields
> dbt test

rem run specific types of tests
> dbt test --schema
> dbt test --data

rem test freshness of source data
> dbt source snapshot-freshness

# Snapshot freshness for all dataset tables:
> dbt source snapshot-freshness --select dbt_bq_example
```

9. Generate documentation for the project:

```cmd
rem sets up the files based on logs from the above run to eventually serve in a static website
> dbt docs generate
```

10. View the documentation for the project:

```cmd
rem launches an easy-to-use static website to navigate data lineage and understand table structures
> dbt docs serve
```

> Note: [dbt style guide](https://github.com/fishtown-analytics/corp/blob/master/dbt_coding_conventions.md)

### What is a jaffle?

A jaffle is a toasted sandwich with crimped, sealed edges. Invented in Bondi in 1949, the humble jaffle is an Australian classic. The sealed edges allow jaffle-eaters to enjoy liquid fillings inside the sandwich, which reach temperatures close to the core of the earth during cooking. Often consumed at home after a night out, the most classic filling is tinned spaghetti, while my personal favourite is leftover beef stew with melted cheese.

---

For more information on dbt:

- Read the [introduction to dbt](https://dbt.readme.io/docs/introduction).
- Read the [dbt viewpoint](https://dbt.readme.io/docs/viewpoint).
- Join the [chat](http://slack.getdbt.com/) on Slack for live questions and support.

---
