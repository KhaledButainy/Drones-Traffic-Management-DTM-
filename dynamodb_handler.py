import boto3

ACCESS_KEY_ID='ASIAQ3QUGVISE3VIUG4V'
ACCESS_SECRET_KEY='1oxHl8XRb7CnbiSmePFDvxzaTYQc6NlzwpWmYq7h'
AWS_SESSION_TOKEN='FwoGZXIvYXdzEN3//////////wEaDP0ELtmauuSGV56LuCJqx4yvjp0m1XlssE6kxzv0L6orRvnrpg0YfN/QKLHCws7HUXLqc41BsBELXgzVeY8aoeS3coh0QJgiveI7hDtNppLkKqD1CIa3gO/+2EuK8UnYkZU91KxS9F3Rpx32SiR6JEYmHJMeo5Sxdijbjv+QBjIozmAOAro8VBWXyxQuE0/naLy7gur67b2GQ2bttrpcQEK2CWTIVTUJtA=='

dynamodb = boto3.resource('dynamodb',
        aws_access_key_id=ACCESS_KEY_ID,
        aws_secret_access_key=ACCESS_SECRET_KEY,
        aws_session_token=AWS_SESSION_TOKEN)

table = dynamodb.create_table(
    TableName='User',
    KeySchema=[
        {
            'AttributeName': 'username',
            'KeyType': 'HASH'
        },{
            'AttributeName': 'email',
            'KeyType': 'RANGE'
        },
         
    ],
    AttributeDefinitions=[
             {
            'AttributeName': 'username',
            'AttributeType': 'S'
        }, {
            'AttributeName': 'email',
            'AttributeType': 'S'
        }, 
    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 5,
        'WriteCapacityUnits': 5
    }
)

