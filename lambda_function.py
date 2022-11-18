import boto3
import json
import logging
from custom_encoder import CustomEncoder

logger = logging.getLogger()
logger.setLevel(logging.INFO)

dynamodbTable = 'product-inventory'
dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table(dynamodbTable)


getMethod = 'GET'
postMethod = 'POST'
patchMethod = 'PATCH'
deleteMethod = 'DELETE'


healthPath = '/health'
userPath = '/user'
usersPath = '/users'
pontosPath = '/registros-ponto'



def lambda_handler(event, context):
    logger.info(event)
    httpMethod = event['httpMethod']
    path = event['path']
    
    if httpMethod == getMethod and path == healthPath:
        response = buildResponse(200)
    
    elif httpMethod == getMethod and path == usersPath:
        response = getUsers()
    
    elif httpMethod == getMethod and path == userPath:
        response = getUser(event['queryStringParameters']['productID'])
        
    elif httpMethod == postMethod and path == userPath:
        response = saveUser(json.loads(event['body']))
    
    elif httpMethod == patchMethod and path == userPath:
        requestBody = json.loads(event['body'])
        response = modifyUser(requestBody['productID'], requestBody['updateKey'], requestBody['updateValue'])
    
    elif httpMethod == deleteMethod and path == userPath:
        requestBody = json.loads(event['body'])
        response = deleteUser(requestBody['productID'])
    
    else:
        response = buildResponse(404, 'Not Found')
    
    return response



def getUser(productID):
    try:
        response = table.get_item(
            Key={
                'productID': productID,
            }
        )
        
        if 'Item' in response:
            return buildResponse(200, response['Item'])
        
        else:
            return buildResponse(400, {'Message': 'ProductID: %s not found' % productID})
        
    except:
        logger.exception('Do your custom error handling here. I am just gonna log it out here')


def getUsers():
    try:
        response = table.scan()
        result = response['Items']
        
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            result.extend(response['Items'])
        
        body = {
            'productID': response
        }
        
        return buildResponse(200, body)
    
    except:
        logger.exception('Do your custom error handling here. I am just gonna log it out here')


def saveUser(requestBody):
    try:
        table.put_item(Item=requestBody)
        
        body = {
            'Operation': 'SAVE',
            'Message': 'SUCCESS',
            'Item': requestBody
        }
        
        return buildResponse(200, body)
    
    except:
        logger.exception('Do your custom error handling here. I am just gonna log it out here')


def modifyUser(productID, updateKey, updateValue):
    try:
        response = table.update_item(
            Key={
                'productID': productID
            },
            UpdateExpression=' set %s = :value' % updateKey,
            ExpressionAtritbuteValues={
                ':value' : updateValue
            },

            ReturnValues='UPDATED_NEW'
        )

        body = {
            'Operation': 'UPDATE',
            'Message': 'SUCCESS',
            'UpdateAttributes': response
        }  

        return buildResponse(200, body)

    
    except:
        logger.exception('Do your custom error handling here. I am just gonna log it out here')


def deleteUser(productID):
    try:
        response = table.delete_item(
            Key={
                'productID': productID
            },
            ReturnValues='ALL_OLD'
        )

        body = {
            'Operation': 'DELETE',
            'Message': 'SUCCESS',
            'deletedItem': response
        }

        return buildResponse(200, body)

    except:
        logger.exception('Do your custom error handling here. I am just gonna log it out here')



def buildResponse(statusCode, body=None):
    response = {
        'statusCode': statusCode,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
        }
    }
    
    if body is not None:
        response['body'] = json.dumps(body, cls=CustomEncoder)
    
    return response