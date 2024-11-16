import json
import random
from datetime import datetime, timedelta

account_costs = {}
accounts_data = []

def mock_get_all_accounts_with_tags():

    # If sample data already exists, return it
    if accounts_data:
        return accounts_data

    # More creative account names
    sample_account_names = [
        "Software Component", 
        "Shared Services", 
        "Networking", 
        "Security", 
        "Data Analytics", 
        "Machine Learning", 
        "DevOps Pipeline", 
        "Cloud Management",
        "User Services", 
        "Storage Management",
        "CI/CD Runners",
        "Data Storage"
    ]
    
    # Probability setup for account status (95% active)
    status_distribution = ["ACTIVE"] * 95 + ["SUSPENDED", "PENDING"]
    sample_domains = ["nowherecompany.com", "examplecorp.com", "mockorganization.org"]
    
    # Sample first and last names to construct 10 unique emails
    first_names = ["John", "Jane", "Alice", "Bob", "Charlie", "Eve", "Mike", "Anna", "Paul", "Sarah"]
    last_names = ["Doe", "Smith", "Johnson", "Williams", "Brown", "Davis", "Taylor", "Anderson", "White", "Moore"]

    # Pre-generate 10 unique owner emails
    owner_emails = [
        f"{first.lower()}.{last.lower()}@{random.choice(sample_domains)}"
        for first, last in zip(first_names, last_names)
    ]

    # Generate mock accounts
    for i in range(1, 11):  # Simulate 10 accounts
        account_id = f"1234567890{i:02}"  # Format IDs for consistent length
        account_name = random.choice(sample_account_names)
        account_status = random.choice(status_distribution)
        joined_timestamp = datetime.now() - timedelta(days=random.randint(100, 1000))

        # Create account information
        account_info = {
            'Id': account_id,
            'Name': account_name,
            'Status': account_status,
            'JoinedTimestamp': joined_timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            'Tags': {}
        }

        # Randomly assign one of the 10 pre-generated owner emails
        owner_email = random.choice(owner_emails)
        
        sample_tags = {
            "Environment": random.choice(["dev", "prod", "test"]),
            "Owner": owner_email,
            "Project": random.choice(["ProjectX", "ProjectY", "ProjectZ", "ProjectAlpha"]),
            "Department": random.choice(["IT", "Finance", "HR", "R&D"]),
            "Region": random.choice(["us-east-1", "eu-west-1", "ap-south-1"])
        }

        # Simulate adding tags to the account
        account_info['Tags'] = sample_tags

        accounts_data.append(account_info)

    return accounts_data


# Function to mock the cost data for a specific account and time period
def mock_get_cost_for_period(start_date, end_date, linked_account_id=None):
    # Ensure start_date and end_date are in the correct format
    start_date = datetime.strptime(start_date, '%Y-%m-%d').strftime('%Y-%m-%d')
    end_date = datetime.strptime(end_date, '%Y-%m-%d').strftime('%Y-%m-%d')

    # Check if a cost for the account already exists
    if linked_account_id not in account_costs:
        # If not, assign a random cost between $100 and $5000 and store it
        account_costs[linked_account_id] = round(random.uniform(100.0, 5000.0), 2)
    
    # Retrieve the cost for the account
    mock_cost = account_costs[linked_account_id]
    
    # Mock response
    response = {
        'ResultsByTime': [
            {
                'TimePeriod': {
                    'Start': start_date,
                    'End': end_date
                },
                'Total': {
                    'UnblendedCost': {
                        'Amount': str(mock_cost),
                        'Unit': 'USD'
                    }
                }
            }
        ]
    }
    
    return response
