from datetime import datetime
from typing import List

from dagster import (
    AssetMaterialization,
    AssetSelection,
    Nothing,
    OpExecutionContext,
    ScheduleDefinition,
    String,
    asset,
    define_asset_job,
    load_assets_from_current_module,
)
from workspaces.types import Aggregation, Stock


@asset(
    config_schema={"s3_key": String},
    required_resource_keys={"s3"},
    op_tags={"kind": "S3"},
)
def get_s3_data(context):
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


@asset
def process_data(get_s3_data):
    stocks = get_s3_data
    max_high = max(stocks, key=lambda x: x.high)
    agg_stock = Aggregation(date=max_high.date, high=max_high.high)
    return agg_stock


@asset(
    required_resource_keys={"redis"},
    op_tags={"kind": "Redis"},
)
def put_redis_data(context, process_data):
    date_highest = str(process_data.date)
    stock_highest = str(process_data.high)
    context.resources.redis.put_data(
        name = date_highest,
        value = stock_highest
        )


@asset(
    required_resource_keys={"s3"},
    op_tags={"kind": "S3"},
)
def put_s3_data(context, process_data):
    key_name = "prefix/stock_1.csv.csv"
    context.resources.s3.put_data(
        key_name = key_name,
        data = process_data)


project_assets = load_assets_from_current_module(
    group_name="week_4_assets",)


machine_learning_asset_job = define_asset_job(
    name="machine_learning_asset_job",
    selection=AssetSelection.groups("week_4_assets"),
    config={"ops": {"get_s3_data": {"config": {"s3_key": "prefix/stock_1.csv"}}}},
)

machine_learning_schedule = ScheduleDefinition(job=machine_learning_asset_job, cron_schedule="*/15 * * * *")
