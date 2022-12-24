import boto3

def add_in_tg(tg_arn,instance_id):
    elb_client = boto3.client('elbv2')
    response = elb_client.register_targets(
    TargetGroupArn=tg_arn,
    Targets=[
        {'Id': instance_id},
        ]
    )
    return(response)