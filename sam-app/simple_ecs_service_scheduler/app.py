#!/usr/bin/python3

"""
Simple service scheduler for ECS. Queries out all running clusters. For each cluster, describes services and their tags.
If tag NoAutoOff is set, will skip action on the service, else will update the service.
If the tag DesiredCountUp is set to n, will update the service to desiredcount n at 7am.
If the tag DesiredCountDown is set to n, will update the service to desiredcount n at 7pm.
Cloudwatch rules will fire 2 events called 7amweekdays and 7pmweekdays every workday to trigger the scaling up and scaling down.
Their json payload is:
{'rulename': '7amweekdays', 'behavior': 'scaleup'}
{'rulename': '7pmweekdays', 'behavior': 'scaledown'}
Does not support setting times, since it is running stateless

Sample input:
{'rulename': '7amweekdays', 'behavior': 'scaledown'}
"""

import boto3
import json

def lambda_handler(event, context):
    print("Running on boto3: " + boto3.__version__)
    behavior = event['behavior']
    print("Behavior set to: " + behavior)
    region = context.invoked_function_arn.split(":")[3]
    if region == None:
        region="eu-west-1"
    print("Region set to: " + region)
    client = boto3.client('ecs', region_name=region)

    # list clusters
    cluster_arns = []
    response = client.list_clusters(
    )
    cluster_arns += response['clusterArns']
    while "nextToken" in response:
        response = client.list_clusters(
            nextToken=response['nextToken']
        )
        cluster_arns += response['clusterArns']
    print("Found the following cluster ARNs:" + str(cluster_arns))

    # get all services per cluster in a dict, that has clusterarn as key, and a list of service arns as values
    service_footprint={}
    for cluster_arn in cluster_arns:
        service_arns=[]
        if cluster_arn in ["arn:aws:ecs:eu-west-1:714079672139:cluster/pnltecs-t01ew1xx-003","arn:aws:ecs:eu-west-1:714079672139:cluster/pnltecs-t01ew1xx-004"] # for now, only take action on these 2 clusters
            response = client.list_services(cluster=cluster_arn)
            service_arns += response['serviceArns']
            while "nextToken" in response:
                response = client.list_services(
                    nextToken=response['nextToken'],
                    cluster=cluster_arn
                )
                service_arns += response['serviceArns']
            service_footprint[cluster_arn] = service_arns

    print("Found the following service footprint:")
    print(json.dumps(service_footprint))

    # a for loop thru all the services per cluster, that checks their tag and if set, updates accordingly
    for key, value in service_footprint.items():
        cluster_arn = key
        service_arns = value
        for service_arn in service_arns:
            print("Checking: " + service_arn)
            response = client.describe_services(
                cluster=cluster_arn,
                services=[
                    service_arn,
                ],
                include=[
                    'TAGS',
                ]
            )
            response = response["services"]
            response = response[0]
            print(str(response))
            print("Checking if Tags are supported yet for service: " + response['serviceArn'])
            if "tags" in response:
                print("Tags set for service: " + response['serviceArn'])
                if "NoAutoOff" not in response['tags'] and behavior == 'scaledown':
                    if "DesiredCountDown" in response['tags']:
                        desiredcount = response['tags']['DesiredCountDown']
                    else:
                        desiredcount = 0
                    response = client.update_service(
                        cluster=cluster_arn,
                        service=service_arn,
                        desiredCount=desiredcount
                    )
                    print("Scaled down: " + service_arn)
                elif "NoAutoOff" not in response['tags'] and behavior == 'scaleup':
                    if "DesiredCountUp" in response['tags']:
                        desiredcount = response['tags']['DesiredCountUp']
                    else:
                        desiredcount = 1
                    response = client.update_service(
                        cluster=cluster_arn,
                        service=service_arn,
                        desiredCount=desiredcount
                    )
                    print("Scaled up: " + service_arn + "to desiredcount " + str(desiredcount))
                else:
                    print("Ignoring " + service_arn + "...")
                    continue
            else:
                print("Tags not supported yet for service: " + response['serviceArn'])
                continue
