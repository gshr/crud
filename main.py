import os
import boto3
from dotenv import load_dotenv
import json
import random
from fastapi import FastAPI, Depends, HTTPException, status
import schemas
from mangum import Mangum
# Testing cloud spaces
app = FastAPI()

load_dotenv()

DB = boto3.resource(
    'dynamodb',
    aws_access_key_id=os.getenv("ACCESS_KEY"),
    aws_secret_access_key=os.getenv("SECRET_KEY")
)


def get_session():
    yield DB


__TableName__ = 'Person'
PRIMARY_KEY = 'ID'
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
    data['ID'] = val

    response = table.put_item(
        Item=data
    )
    response = table.get_item(Key={
        PRIMARY_KEY: val,
    })

    return response['Item']


@app.delete('/data/{id}')
async def deleteData(id, dynamodb=Depends(get_session)):
    table = dynamodb.Table(__TableName__)
    response = table.delete_item(Key={
        PRIMARY_KEY: id,
    })
    if response['ResponseMetadata']['HTTPStatusCode'] == 200:
        return {'detail': 'Item Deleted Successfully'}


@app.put('/data/{id}')
async def updateData(id, item: schemas.UserInfo, dynamodb=Depends(get_session)):
    table = dynamodb.Table(__TableName__)
    print(item)
    print(id)
    data = item.dict()
    # response = table.update_item(
    #     Item=data
    # )

    response = table.get_item(Key={
        PRIMARY_KEY: id,
    })

    if 'Item' in response:
        resp = table.update_item(Key={
            PRIMARY_KEY: id
        }, UpdateExpression="SET COUNTRY= :c , ADDRESS = :a , AGE= :age ",
            ExpressionAttributeValues={':c': item.COUNTRY,
                                       ':a': item.ADDRESS,
                                       ':age': item.AGE},

            ReturnValues="UPDATED_NEW"
        )

        return resp['Attributes']

    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                        detail=f"User with id {id} was not found")


handler = Mangum(app)
