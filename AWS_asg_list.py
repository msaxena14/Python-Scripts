import boto3

session = boto3.Session()

service_object = boto3.client('autoscaling','ap-south-1')

class AutoScaling:
    def __init__(self, a_name, a_in, a_lb, a_lb_tg, a_tags):
        self.name = a_name
        self.instance = a_in
        self.load_balancer = a_lb
        self.load_balancer_target_group = a_lb_tg
        self.tags = a_tags

response = service_object.describe_auto_scaling_groups(
    AutoScalingGroupNames=[],
    MaxRecords=100,
)



print(len(response))
