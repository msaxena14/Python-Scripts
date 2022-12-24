import boto3
def scale_in_protection(asg_name,instances,scale_in):
    asg_object = boto3.client('autoscaling')
    asg_object.set_instance_protection(
        InstanceIds=instances,
        AutoScalingGroupName=asg_name, 
        ProtectedFromScaleIn=scale_in
    )