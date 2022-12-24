import boto3

def values(asg_name,template_name,default_version,minimum_healthy_percentage):
    asg = boto3.client('autoscaling')
    response = asg.start_instance_refresh(
        AutoScalingGroupName=asg_name,
        Strategy='Rolling',
        DesiredConfiguration={
            'LaunchTemplate': {
                'LaunchTemplateName': template_name,
                'Version': str(default_version)
            },
        },
        Preferences={
            'InstanceWarmup': 300,
            'MinHealthyPercentage': minimum_healthy_percentage,
            'SkipMatching': False,
        }
    )
    print(response)