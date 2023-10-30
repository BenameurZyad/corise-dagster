import sys
sys.path.append("/workspace/corise-dagster/week_2/")

from typing import Optional
from random import randint

from dagster import (
    In,
    Nothing,
    OpExecutionContext,
    Out,
    Output,
    ResourceDefinition,
    String,
    graph,
    op,
)
from dagster_dbt import dbt_cli_resource, dbt_run_op, dbt_test_op, DbtCliOutput
from workspaces.config import ANALYTICS_TABLE, DBT, POSTGRES
from workspaces.resources import postgres_resource


@op(
    config_schema={"table_name": String},
    out=Out(String),
    required_resource_keys={"database"},
    tags={"kind": "postgres"},
)
def create_dbt_table(context: OpExecutionContext):
    table_name = context.op_config["table_name"]
    schema_name = table_name.split(".")[0]
    sql = f"CREATE SCHEMA IF NOT EXISTS {schema_name};"
    context.resources.database.execute_query(sql)
    sql = f"CREATE TABLE IF NOT EXISTS {table_name} (column_1 VARCHAR(100), column_2 VARCHAR(100), column_3 VARCHAR(100));"
    context.resources.database.execute_query(sql)
    return table_name


@op(
    ins={"table_name": In(dagster_type=String)},
    out=Out(Nothing),
    required_resource_keys={"database"},
    tags={"kind": "postgres"},
)
def insert_dbt_data(context: OpExecutionContext, table_name: String):
    sql = f"INSERT INTO {table_name} (column_1, column_2, column_3) VALUES ('A', 'B', 'C');"

    number_of_rows = randint(1, 100)
    for _ in range(number_of_rows):
        context.resources.database.execute_query(sql)
        context.log.info("Inserted a row")

    context.log.info("Batch inserted")


@op(
    # config_schema={"s3_key": String },
    # out={"stocks": Out(dagster_type=DbtCliOutput)},
    required_resource_keys={"dbt"},
    tags={"kind": "dbt"}
)
def dbt_run(context: OpExecutionContext):
    # dbt_run_object = dbt_cli_resource(context).run()
    # dbt_run_logs = dbt_run_object.logs()
    context.resources.dbt.run()
    context.log.info("Finish running dbt")
    return True

@op(
    # config_schema={"s3_key": String },
    # out={"stocks": Out(dagster_type=DbtCliOutput)},
    required_resource_keys={"dbt"},
    out={"success": Out(is_required=False), "failure": Out(is_required=False)},
    tags={"kind": "dbt"}
)
def dbt_test(context: OpExecutionContext, _start: bool):
    returncode = context.resources.dbt.test()

    if returncode == 0: yield Output(1, "success")
    else: yield Output(2, "failure")



@op
def success_run(context: OpExecutionContext, _start):
    context.log.info("Success!")

@op
def failure_run(context: OpExecutionContext, _start):
    context.log.info("Failure!")


@graph
def dbt():

    finish = insert_dbt_data(create_dbt_table())

    success, failure = dbt_test(dbt_run())

    success_run(success)
    failure_run(failure)


docker = {
    "resources": {
        "database": {"config": POSTGRES},
        "dbt": {"config": DBT},
    },
    "ops": {"create_dbt_table": {"config": {"table_name": ANALYTICS_TABLE}}},
}

dbt_docker = dbt.to_job(
    name="dbt_docker",
    config=docker,
    resource_defs={
        "database": postgres_resource,
        "dbt": dbt_cli_resource,
    },
)
