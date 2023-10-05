import csv
from datetime import datetime
from heapq import nlargest
from typing import Iterator, List

from dagster import (
    Any,
    DynamicOut,
    DynamicOutput,
    In,
    Nothing,
    OpExecutionContext,
    Out,
    Output,
    String,
    job,
    op,
    usable_as_dagster_type,
)
from pydantic import BaseModel


@usable_as_dagster_type(description="Stock data")
class Stock(BaseModel):
    date: datetime
    close: float
    volume: int
    open: float
    high: float
    low: float

    @classmethod
    def from_list(cls, input_list: List[str]):
        """Do not worry about this class method for now"""
        return cls(
            date=datetime.strptime(input_list[0], "%Y/%m/%d"),
            close=float(input_list[1]),
            volume=int(float(input_list[2])),
            open=float(input_list[3]),
            high=float(input_list[4]),
            low=float(input_list[5]),
        )


@usable_as_dagster_type(description="Aggregation of stock data")
class Aggregation(BaseModel):
    date: datetime
    high: float


def csv_helper(file_name: str) -> Iterator[Stock]:
    with open(file_name) as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            yield Stock.from_list(row)


@op(
    config_schema={"s3_key": String}, 
    out={
        "stocks": Out(is_required=False, dagster_type=List[Stock]),
        "empty_stocks": Out(is_required=False, dagster_type=Any),
    }, 
    description="Get a list of stocks from an S3 file"
)
def get_s3_data_op(context) -> List[Stock]:
    file_name = context.op_config["s3_key"]
    stock_data = list(csv_helper(file_name))
    if len(stock_data) != 0:
        yield Output(stock_data, "stocks")
    else :
        yield Output(None, "empty_stocks")


@op(
    config_schema={"nlargest": int}, 
    out=DynamicOut(dagster_type=Aggregation), 
    description="Given a list of stocks return the Aggregation with the greatest high value"
)
def process_data_op(context, stocks: List[Stock]) -> Aggregation:
    N_values = context.op_config["nlargest"]
    top_N_stocks = sorted(stocks, key=lambda stock: stock.high, reverse=True)[:N_values]
    for i in range(len(top_N_stocks)):
        _stock = top_N_stocks[i]
        agg_stock = Aggregation(date=_stock.date, high=_stock.high)
        yield DynamicOutput(agg_stock, mapping_key=str(i))

@op(
    out=Out(dagster_type=Nothing),
    description="Upload an Aggregation to Redis"
)
def put_redis_data_op(aggregation: Aggregation) -> Nothing:
    my_agg_stock = aggregation
    pass


@op(
    out=Out(dagster_type=Nothing),
    description="Upload an Aggregation to S3 file"
)
def put_s3_data_op(aggregation: Aggregation) -> Nothing:
    my_agg_stock = aggregation
    pass


@op(
    ins={"empty_stocks": In(dagster_type=Any)},
    out=Out(dagster_type=Nothing),
    description="Notifiy if stock list is empty"
)
def empty_stock_notify_op(context: OpExecutionContext, empty_stocks: Any):
    context.log.info("No stocks returned")


@job(
    config={"ops":
        {"get_s3_data_op": {"config": {"s3_key": "week_1/data/stock.csv"}},
        "process_data_op": {"config": {"nlargest": 5}}}}
)
def machine_learning_dynamic_job():
    stocks, empty_stocks = get_s3_data_op()
    empty_stock_notify_op(empty_stocks)
    dynamic_stocks = process_data_op(stocks)
    dynamic_stocks.map(put_redis_data_op)
    dynamic_stocks.map(put_s3_data_op)
