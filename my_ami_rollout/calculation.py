import boto3
import scale_in_protection as scaling
import instance_refresh as updating
import health_check_tg as health_check_utility
import update_asg_count as update_count

def asg_count_update(asg_name,maxi,mini,desired,list_of_old_instances,template_name,template_id,new_version,minimum_healthy_percentage,TargetGroupARNs):
    minimum_healthy_percentage = calculate_minimum_healthy_percentage()
    if(desired > 2):
        for i in range(desired):
            scaling.scale_in_protection(asg_name,list_of_old_instances[i],False)
            updating.values(asg_name,template_name,new_version,minimum_healthy_percentage)
            list_of_new_instances = asg_details()
            new_instance_after_refresh = list(set(list_of_new_instances) - set(list_of_old_instances))
            list_of_old_instances.append(new_instance_after_refresh[i])
            health_check_utility.health_check(TargetGroupARNs,new_instance_after_refresh[i],asg_name,template_name,new_version,minimum_healthy_percentage)
            scaling.scale_in_protection(asg_name,new_instance_after_refresh[i],True)
    else:
        for i in range(desired):
            if(maxi == desired):
                desired = desired + 1
                maxi = maxi + 1
            elif(desired < maxi):
                desired = desired + 1
            update_count.update_asg_count(asg_name,template_id,new_version,mini,maxi,desired)
            asg_details(asg_name,desired,list_of_old_instances,list_of_new_instances)
            new_instance_after_refresh = set(list_of_new_instances) - set(list_of_old_instances)
            health_check_utility.health_check(TargetGroupARNs,new_instance_after_refresh)
            scaling.scale_in_protection(asg_name,new_instance_after_refresh,True)

def calculate_minimum_healthy_percentage(self):
    return(int(100 - ((1 / self.desired) * 100)))

def asg_details(asg_name,desired,count):
    list_of_instances = []
    asg_object = boto3.client('autoscaling')
    response = asg_object.describe_auto_scaling_groups(
        AutoScalingGroupNames=asg_name
    )    
    for i in range(desired):
        list_of_instances.append(response['AutoScalingGroups'][0]['Instances'][i]['InstanceId'])
    TargetGroupARNs = response['AutoScalingGroups'][0]['TargetGroupARNs']
    if count == 1:
        return(list_of_instances,TargetGroupARNs)
    else:
        return(list_of_instances)