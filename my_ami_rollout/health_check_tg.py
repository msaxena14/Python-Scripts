import boto3
import instance_refresh as updating
import calculation as calc
import part_of_tg as registered

def health_check(tg_arn,instance_id,asg_name,template_name,new_version,minimum_healthy_percentage,list_of_old_instances,desired,count):
    new_instance_after_refresh = []
    elb_client = boto3.client('elbv2')
    response = elb_client.describe_target_health(TargetGroupArn=tg_arn,
    Targets=[
        {
            'Id': instance_id
        },
    ])
    status = (response['TargetHealthDescriptions'][0]['TargetHealth']['State'])
    reason = (response['TargetHealthDescriptions'][0]['TargetHealth']['Reason'])
    if(status == 'unhealthy'):
        if(reason == 'Target.NotRegistered'):
            registered.add_in_tg(tg_arn,instance_id)
            health_check(tg_arn,new_instance_after_refresh[0],asg_name,template_name,new_version,minimum_healthy_percentage,list_of_old_instances,desired,count)
        else:
            if(count < 2):
                updating.values(asg_name,template_name,new_version,minimum_healthy_percentage)
                list_of_new_instances = calc.asg_details(asg_name,desired)
                temp = list(set(list_of_new_instances) - set(list_of_old_instances))
                new_instance_after_refresh.append(temp[0])
                count = count + 1
                health_check(tg_arn,new_instance_after_refresh[0],asg_name,template_name,new_version,minimum_healthy_percentage,list_of_old_instances,desired,count)
            else:
                print("Exceede number of retries, Aborting Activity")
                exit(0)
    else:
        return(instance_id)