import boto3
import update_asg_count as another_utility

def values(asg_name,template_id,template_name,default_version,mini,desired,maxi):
    for i in range(desired):
        if(desired == maxi):
            maxi = maxi + 1
            desired = desired + 1
            change(asg_name,template_id,template_name,default_version,mini,maxi,desired)
        if(desired < maxi):
            desired = desired + 1
            change(asg_name,template_id,template_name,default_version,mini,maxi,desired)

def change(asg_name,template_id,template_name,default_version,mini,maxi,desired):
    print("Mini: %s Maxi: %s Desired: %s"%(mini, maxi, desired))
    print("ASGNAME %s TemplateID: %s TemplateName: %s Default_version: %s" %(asg_name,template_id,template_name,default_version))
    another_utility.update_asg_count(asg_name,template_id,template_name,default_version,mini,maxi,desired)