import os
import boto3
from dotenv import load_dotenv
import json
import random
from fastapi import FastAPI, Depends, HTTPException, status
import schemas

app = FastAPI(

)

load_dotenv()

DB = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv("ACCESS_KEY"),
    aws_secret_access_key=os.getenv("SECRET_KEY"),
)


def get_session():
    yield DB


__TableName__ = 'Person'
PRIMARY_KEY = 'ADDHAR_ID'
columns = ['AGE', 'NAME']


#
# response = table.get_item(
#     Key={
#         PRIMARY_KEY: 21346
#     }
# )
#
# print(response)
# @app.get("/data")
# def hello():
#     return {"result": "Hello"}


def list_all_tables():
    tables = list(DB.tables.all())
    print(tables)


@app.get("/data")
def getTableData(dynamodb=Depends(get_session)):
    table = dynamodb.Table(__TableName__)
    response = table.scan()
    data = response['Items']
    return data


@app.get("/data/{id}")
def getKey(id, dynamodb=Depends(get_session)):
    print(id)
    table = dynamodb.Table(__TableName__)
    response = table.get_item(Key={
        PRIMARY_KEY: str(id),
    })
    if "Item" in response:
        return response['Item']
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User with id {id} was not found")


@app.post("/data")
def addinfo(item: schemas.UserInfo, dynamodb=Depends(get_session)):
    table = dynamodb.Table(__TableName__)
    print(item)
    data = item.dict()
    val = str(random.randint(1000, 100000000))
    data['ADDHAR_ID'] = val

    response = table.put_item(
        Item=data
        # PRIMARY_KEY: str(random.randint(1000, 100000000)),
        # 'NAME': fake.name(),
        # 'ADDRESS': fake.address(),
        # 'AGE': random.randint(20, 100),
        # 'COUNTRY': fake.country()

    )

    response = table.get_item(Key={
        PRIMARY_KEY: val,
    })

    return response['Item']

