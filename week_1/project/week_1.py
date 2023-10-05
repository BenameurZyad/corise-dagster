import csv
from datetime import datetime
from typing import Iterator, List

from dagster import (
    In,
    Nothing,
    OpExecutionContext,
    Out,
    String,
    job,
    op,
    graph,
    usable_as_dagster_type,
    DynamicOut, 
    DynamicOutput
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


@op(config_schema={"s3_key": String}, 
    out={"stocks": Out(dagster_type=List[Stock])}, 
    description="Get a list of stocks from an S3 file",
    tags={"category": "s3"})
def get_s3_data_op(context) -> List[Stock]:
    file_name = context.op_config["s3_key"]
    stock_data = list(csv_helper(file_name))
    return stock_data


@op(out={"aggregation": Out(dagster_type=Aggregation)}, 
    description="Given a list of stocks return the Aggregation with the greatest high value")
def process_data_op(stocks: List[Stock]) -> Aggregation:
    max_high = max(stocks, key=lambda x: x.high)
    agg_stock = Aggregation(date=max_high.date, high=max_high.high)
    return agg_stock


@op(
    #out=Out(Nothing),
    description="Upload an Aggregation to Redis",
    tags={"category": "redis"})
def put_redis_data_op(aggregation: Aggregation) -> Nothing:
    my_agg_stock = aggregation
    pass


@op(
    #out=Out(Nothing),
    description="Upload an Aggregation to S3 file",
    tags={"category": "s3"})
def put_s3_data_op(aggregation: Aggregation) -> Nothing:
    my_agg_stock = aggregation
    pass


@job(config={"ops": {"get_s3_data_op": {"config": {"s3_key": "week_1/data/stock.csv"}}}})
def machine_learning_job():
    my_data = process_data_op(get_s3_data_op())
    put_redis_data_op(my_data)
    put_s3_data_op(my_data)

