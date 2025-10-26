import json
import boto3
import requests
import hashlib
from datetime import datetime, timedelta
import os
from decimal import Decimal

# Initialize DynamoDB client
dynamodb = boto3.resource('dynamodb')
table_name = os.environ.get('DYNAMODB_TABLE_NAME', 'ApiDataCache')
table = dynamodb.Table(table_name)

# API configuration
API_KEY = os.environ.get('API_KEY')
API_ENDPOINT = os.environ.get('API_ENDPOINT')

def decimal_default(obj):
    """Helper function to serialize Decimal objects"""
    if isinstance(obj, Decimal):
        return float(obj)
    raise TypeError

def generate_data_hash(data):
    """Generate a unique hash for the data to prevent duplicates"""
    data_string = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_string.encode()).hexdigest()

def fetch_api_data():
    """Fetch data from external API"""
    headers = {
        'Authorization': f'Bearer {API_KEY}',
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.get(API_ENDPOINT, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching API data: {e}")
        raise

def store_data_with_ttl(data_item):
    """Store data in DynamoDB with 3-day TTL"""
    # Generate unique ID for the data
    data_hash = generate_data_hash(data_item)
    
    # Calculate TTL (3 days from now)
    ttl_timestamp = int((datetime.now() + timedelta(days=3)).timestamp())
    
    # Check if item already exists
    try:
        response = table.get_item(Key={'data_id': data_hash})
        if 'Item' in response:
            print(f"Data with hash {data_hash} already exists, skipping...")
            return False
    except Exception as e:
        print(f"Error checking existing data: {e}")
    
    # Store new data
    try:
        table.put_item(
            Item={
                'data_id': data_hash,
                'data': data_item,
                'created_at': datetime.now().isoformat(),
                'ttl': ttl_timestamp,
                'fetch_timestamp': int(datetime.now().timestamp())
            }
        )
        print(f"Successfully stored data with hash {data_hash}")
        return True
    except Exception as e:
        print(f"Error storing data: {e}")
        raise

def get_cached_data():
    """Retrieve all non-expired cached data"""
    try:
        # Scan for all items (DynamoDB will automatically filter expired TTL items)
        response = table.scan()
        items = response.get('Items', [])
        
        # Handle pagination if needed
        while 'LastEvaluatedKey' in response:
            response = table.scan(ExclusiveStartKey=response['LastEvaluatedKey'])
            items.extend(response.get('Items', []))
        
        return items
    except Exception as e:
        print(f"Error retrieving cached data: {e}")
        raise

def lambda_handler(event, context):
    """Main Lambda handler function"""
    
    # Determine the action from the event
    http_method = event.get('httpMethod', 'GET')
    path = event.get('path', '/fetch')
    
    try:
        if http_method == 'POST' and path == '/fetch-new':
            # Fetch new data from API and store it
            api_data = fetch_api_data()
            
            # Handle both single items and arrays of items
            if isinstance(api_data, list):
                stored_count = 0
                for item in api_data:
                    if store_data_with_ttl(item):
                        stored_count += 1
                
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'message': f'Successfully processed {len(api_data)} items',
                        'new_items_stored': stored_count,
                        'duplicates_skipped': len(api_data) - stored_count
                    })
                }
            else:
                # Single item
                is_new = store_data_with_ttl(api_data)
                return {
                    'statusCode': 200,
                    'headers': {
                        'Content-Type': 'application/json',
                        'Access-Control-Allow-Origin': '*'
                    },
                    'body': json.dumps({
                        'message': 'Data processed successfully',
                        'is_new_data': is_new
                    })
                }
        
        elif http_method == 'GET' and path == '/data':
            # Return all cached data to frontend
            cached_data = get_cached_data()
            
            # Extract just the data field from each item
            data_list = [item['data'] for item in cached_data]
            
            return {
                'statusCode': 200,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'data': data_list,
                    'count': len(data_list),
                    'timestamp': datetime.now().isoformat()
                }, default=decimal_default)
            }
        
        else:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*'
                },
                'body': json.dumps({
                    'error': 'Invalid request',
                    'message': 'Supported endpoints: POST /fetch-new, GET /data'
                })
            }
            
    except Exception as e:
        print(f"Lambda execution error: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error',
                'message': str(e)
            })
        }