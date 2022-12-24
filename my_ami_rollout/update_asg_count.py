import boto3

def update_asg_count(asg_name,template_id,version,mini,maxi,desired):
    asg_object = boto3.client('autoscaling')
    response = asg_object.update_auto_scaling_group(
        AutoScalingGroupName=asg_name,
        LaunchTemplate={
            'LaunchTemplateId': template_id,
            'Version': str(version)
        },
        MinSize=mini,
        MaxSize=maxi,
        DesiredCapacity=desired,
    )
    print("update_asg_count %s" % response)