#!/usr/bin/python3

"""
Simple service scheduler for ECS. Queries out all running clusters. For each cluster, describes service tags.
If the tag desiredofficehours is set to n, will update the service to desiredcount n at 7am.
CLoudwatch rules will fire an event called 7amweekdays
If the tag desiredoutofofficehours is set to n, will update the service to desiredcount n at 7pm.
CLoudwatch rules will fire an event called 7pmweekdays
Does not support setting times, since it is running stateless

Sample input:
{
    "version": "0",
    "id": "53dc4d37-cffa-4f76-80c9-8b7d4a4d2eaa",
    "detail-type": "Scheduled Event",
    "source": "aws.events",
    "account": "123456789012",
    "time": "2015-10-08T16:53:06Z",
    "region": "us-east-1",
    "resources": [
        "arn:aws:events:us-east-1:123456789012:rule/my-scheduled-rule"
    ],
    "detail": {}
}
"""

import boto3

def lambda_handler(event, context):

    # Get Account ID from lambda function arn in the context
    ACCOUNT_ID = context.invoked_function_arn.split(":")[4]
