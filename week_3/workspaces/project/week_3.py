from datetime import datetime
from typing import List

from dagster import (
    AssetMaterialization,
    In,
    Nothing,
    OpExecutionContext,
    Out,
    ResourceDefinition,
    RetryPolicy,
    RunRequest,
    ScheduleDefinition,
    SensorEvaluationContext,
    ScheduleEvaluationContext,
    SkipReason,
    graph,
    op,
    String,
    schedule,
    sensor,
    static_partitioned_config,
)
from workspaces.config import REDIS, S3, S3_FILE
from workspaces.project.sensors import get_s3_keys
from workspaces.resources import mock_s3_resource, redis_resource, s3_resource
from workspaces.types import Aggregation, Stock


@op(
    config_schema={"s3_key": String },
    out={"stocks": Out(dagster_type=List[Stock])},
    required_resource_keys={"s3"},
    tags={"kind": "S3"},
)
def get_s3_data(context: OpExecutionContext) -> List[Stock]:
    s3_key_name = context.op_config["s3_key"]
    stock_data = [Stock.from_list(stock) for stock in context.resources.s3.get_data(s3_key_name)]
    # stock_data = list(context.resources.s3.get_data(s3_key_name))
        # New this week
    context.log_event(
        AssetMaterialization(
            asset_key="Testing Log.",
            description="Getting Data from S3.",
            metadata={"table_name": len(stock_data), "s3_key_name": s3_key_name},
        )
    )

    return stock_data


@op(out={"aggregation": Out(dagster_type=Aggregation)},
    description="Given a list of stocks return the Aggregation with the greatest high value")
def process_data(stocks: List[Stock]) -> Aggregation:
    max_high = max(stocks, key=lambda x: x.high)
    agg_stock = Aggregation(date=max_high.date, high=max_high.high)
    return agg_stock


@op(
    out={"Nothing": Out(dagster_type=Nothing)},
    required_resource_keys={"redis"},
    tags={"kind": "Redis"},
)
def put_redis_data(context: OpExecutionContext, aggregation: Aggregation) -> Nothing:
    date_highest = str(aggregation.date)
    stock_highest = str(aggregation.high)
    context.resources.redis.put_data(
        name = date_highest,
        value = stock_highest
        )


@op(
    out={"Nothing": Out(dagster_type=Nothing)},
    required_resource_keys={"s3"},
    tags={"kind": "S3"},
)
def put_s3_data(context: OpExecutionContext, aggregation: Aggregation):
    key_name = "prefix/stock.csv"
    context.resources.s3.put_data(
        key_name = key_name,
        data = aggregation)


@graph
def machine_learning_graph():
    aggregation = process_data(get_s3_data())
    put_redis_data(aggregation = aggregation)
    put_s3_data(aggregation = aggregation)




local = {"resources": {
        "redis": {"config": REDIS}
    },
    "ops": {"get_s3_data": {"config": {"s3_key": S3_FILE}}},
}

@static_partitioned_config(partition_keys=["1","2","3","4","5","6","7","8","9","10"])
def docker_config(partition_key: str):
    return {
        "resources": {
        "s3": {"config": S3},
        "redis": {"config": REDIS},
        },
      "ops": {"get_s3_data": {"config": {"s3_key": "prefix/stock_" + partition_key + ".csv" }}},
    }


machine_learning_job_local = machine_learning_graph.to_job(
    name="machine_learning_job_local",
    config=local,
    resource_defs={"s3": mock_s3_resource,
                   "redis": redis_resource}
)

machine_learning_job_docker = machine_learning_graph.to_job(
    name="machine_learning_job_docker",
    op_retry_policy=RetryPolicy(max_retries=10, delay=1),
    config=docker_config,
    resource_defs={"s3": s3_resource,
                   "redis": redis_resource}
)


machine_learning_schedule_local = ScheduleDefinition(
    job=machine_learning_job_local, cron_schedule="*/15 * * * *"
    )


# machine_learning_schedule_local = build_schedule_from_partitioned_job(machine_learning_job_docker)

@schedule(job=machine_learning_job_docker, cron_schedule="0 * * * *")
def machine_learning_schedule_docker(context: ScheduleEvaluationContext):
    scheduled_date = context.scheduled_execution_time.strftime("%Y-%m-%d")
    return RunRequest(
        run_key=None,
        run_config={
            "ops": {"configurable_op": {"config": {"scheduled_date": scheduled_date}}}
        },
        tags={"date": scheduled_date},
    )


@sensor(job=machine_learning_job_docker, minimum_interval_seconds=30)
def machine_learning_sensor_docker():
    new_files = get_s3_keys(
        bucket = 'dagster',
        prefix = 'prefix',
        endpoint_url = 'http://localstack:4566'
    )
    if not new_files:
        yield SkipReason("No new s3 files found in bucket.")
        return
    for new_file in new_files:
        yield RunRequest(
            run_key=new_file,
            run_config={"resources": {
                "s3": {"config": S3},
                "redis": {"config": REDIS}
                },
                "ops": {
                    "get_s3_data": {"config": {"s3_key": new_file}}
                },
            },
        )
