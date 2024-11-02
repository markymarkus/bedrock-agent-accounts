import json
import boto3
import os
from datetime import datetime
from mock import mock_get_all_accounts_with_tags, mock_get_cost_for_period 

ce_client = boto3.client('ce')
org_client = boto3.client('organizations')

enable_mock = os.getenv('EnableMock', 'false').lower() == 'true'

def get_cost_for_period(start_date, end_date, linked_account_id=None):
    # Ensure start_date and end_date are in the correct format
    start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d')

    if enable_mock:
        # Call mock function if mock is enabled
        return mock_get_cost_for_period(start_date, end_date, linked_account_id)

    # Create the filter for linked account if provided
    filter_criteria = {
        'Not': {
            'Dimensions': {
                'Key': 'RECORD_TYPE',
                'Values': ['Credit']  # Exclude free credits from the report
            }
        }
    }

    if linked_account_id:
        # Add the linked account filter if provided
        linked_account_filter = {
            'Dimensions': {
                'Key': 'LINKED_ACCOUNT',
                'Values': [linked_account_id]
            }
        }
        # Combine filters: Exclude credits and filter by linked account
        filter_criteria = {
            'And': [filter_criteria, linked_account_filter]
        }

    # Fetch the cost and usage for the specified time period with filtering to exclude credits
    response = ce_client.get_cost_and_usage(
        TimePeriod={
            'Start': start_date,
            'End': end_date
        },
        Granularity='MONTHLY',
        Metrics=['UnblendedCost'],
        Filter=filter_criteria  # Apply the filter to exclude credits
    )

    return response['ResultsByTime']

def get_all_accounts_with_tags():
    if enable_mock:
        # Call mock function if mock is enabled
        return mock_get_all_accounts_with_tags()
        
    accounts_data = []

    # Get all accounts from AWS Organizations
    paginator = org_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        for account in page['Accounts']:
            account_info = {
                'Id': account['Id'],
                'Name': account['Name'],
                'Status': account['Status'],
                'JoinedTimestamp': account['JoinedTimestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'Tags': {}
            }

            # Get tags for the account
            tags_response = org_client.list_tags_for_resource(
                ResourceId=account['Id']
            )
            for tag in tags_response['Tags']:
                account_info['Tags'][tag['Key']] = tag['Value']

            accounts_data.append(account_info)

    return accounts_data

def get_costs(parameters):
    account_id = start_date = end_date = None
    
    # Loop through parameters and extract values
    for param in parameters['parameters']:
        if param['name'] == 'accountId':
            account_id = param['value']
        elif param['name'] == 'start_date':
            start_date = param['value']
        elif param['name'] == 'end_date':
            end_date = param['value']
            
    print(f"Account ID: {account_id}")
    print(f"Start Date: {start_date}")
    print(f"End Date: {end_date}")

    costs = get_cost_for_period(start_date,end_date, account_id)
    response = {'Costs': costs }
    
    return {"response": response}
    
def lambda_handler(event, context):
    print(event)
    agent = event.get('agent', None)
    actionGroup = event.get('actionGroup', None)
    apiPath = event.get('apiPath', None)
    httpMethod = event.get('httpMethod', None)
    parameters = event.get('parameters', [])
    requestBody = event.get('requestBody', {})
    messageVersion = event.get('messageVersion', None)

    responseBody =  {
        "application/json": {
            "body": "The API {} was called successfully!".format(apiPath)
        }
    }
    
    if apiPath == '/accounts':
        body = get_all_accounts_with_tags()
    elif apiPath == '/account/{accountId}/costs':
        body = get_costs(event)

    response_body = {
        'application/json': {
            'body': json.dumps(body)
        }
    }

    action_response = {
        'actionGroup': actionGroup,
        'apiPath': apiPath,
        'httpMethod': httpMethod,
        'httpStatusCode': 200,
        'responseBody': response_body
    }

    response = {'response': action_response}

    print(response)
    
    return response

