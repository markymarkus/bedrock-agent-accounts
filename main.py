import boto3
import json
from datetime import datetime

# Initialize boto3 clients
org_client = boto3.client('organizations')
ce_client = boto3.client('ce')

def get_cost_for_month(year, month, linked_account_id=None):
    # Get the first and last day of the specified month
    start_date = datetime(year, month, 1).strftime('%Y-%m-%d')
    
    # Calculate the end date of the month (last day)
    if month == 12:  # For December, next month is January of the next year
        end_date = datetime(year + 1, 1, 1).strftime('%Y-%m-%d')
    else:
        end_date = datetime(year, month + 1, 1).strftime('%Y-%m-%d')

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

# Function to query all AWS accounts and their tags
def get_all_accounts_with_tags():
    accounts_data = []

    # Get all accounts from AWS Organizations
    paginator = org_client.get_paginator('list_accounts')
    for page in paginator.paginate():
        for account in page['Accounts']:
            account_info = {
                'Id': account['Id'],
                'Name': account['Name'],
                'Email': account['Email'],
                'Status': account['Status'],
                'JoinedTimestamp': account['JoinedTimestamp'].strftime('%Y-%m-%d %H:%M:%S'),
                'Tags': {}
            }

            # Get tags for the account
            tags_response = org_client.list_tags_for_resource(
                ResourceId=account['Id']
            )
            for tag in tags_response['Tags']:
                if tag['Key'] in ['Department', 'Owner', 'Environment']:
                    account_info['Tags'][tag['Key']] = tag['Value']

            accounts_data.append(account_info)

    return accounts_data

# Function to filter accounts based on optional criteria
def filter_dicts(data, owner=None, environment=None, department=None):
    # Filter through the list of dictionaries based on optional parameters
    def matches_criteria(account):
        tags = account.get('Tags', {})
        if owner is not None and tags.get('Owner') != owner:
            return False
        if environment is not None and tags.get('Environment') != environment:
            return False
        if department is not None and tags.get('Department') != department:
            return False
        return True

    # Return a list of dictionaries that match the criteria
    return [account for account in data if matches_criteria(account)]

# Store the account data for the session
accounts_cache = get_all_accounts_with_tags()

# Filter the accounts with owner 'markus.toivakka@puistikko.fi'
r_dict = filter_dicts(accounts_cache, owner="markus.toivakka@puistikko.fi")

# Print the filtered results
for account in r_dict:
    print(json.dumps(account, indent=4))
    cost_data = get_cost_for_month(2024, 9, account['Id'])
    for result in cost_data:
        month = result['TimePeriod']['Start']
        amount = result['Total']['UnblendedCost']['Amount']
        print(f"Month: {month}, Cost for account {account['Id']}: ${amount}")    
