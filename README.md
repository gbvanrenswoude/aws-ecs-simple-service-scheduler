# simple-service-scheduler

A simple MVP ECS service scheduler.

----
Simple service scheduler for ECS. Queries out all running clusters. For each cluster, describes services and their tags.  
If tag AutoOff is set, will take action on the service.  
If the tag DesiredCountUp is set to n, will update the service to desiredcount n at 7am.  
If the tag DesiredCountDown is set to n, will update the service to desiredcount n at 7pm.  
Cloudwatch rules will fire 2 events called 7amweekdays and 7pmweekdays every workday to trigger the scaling up and scaling down.  
Their json payload is:  
`{'rulename': '7amweekdays', 'behavior': 'scaleup'}`  
`{'rulename': '7pmweekdays', 'behavior': 'scaledown'}`  
Does not support setting times, since it is running stateless  
Sample input:  
`{'rulename': '7amweekdays', 'behavior': 'scaledown'}`
----