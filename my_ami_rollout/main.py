import boto3
import create_launch_template_version as utility
import scale_in_protection as scaling
import instance_refresh as updating
import health_check_tg as health_check_utility
import update_asg_count as update_count
import calculation as calc
import part_of_tg as registerd


class asg():
    def __init__(self):
        self.asg_name = "Default"
        self.template_id = "Default"
        self.template_name = "Default"
        self.list_of_old_instances = []
        self.list_of_new_instances = []
        self.desired = ""
        self.mini = ""
        self.maxi = ""
        self.default_version = ""
        self.latest_version = ""
        self.new_version = ""
        self.TargetGroupARNs = ""
        self.flag_for_asg_details = 0
        self.flag_for_scale_in = 0
        self.new_instance_after_refresh = []
        self.old_mini , self.old_maxi , self.old_desired = "" , "" , ""

    def get_name(self,name):
        self.asg_name = name
        asg_object = boto3.client('autoscaling')
        response = asg_object.describe_auto_scaling_groups(
            AutoScalingGroupNames=name
        )
        required_info = response['AutoScalingGroups'][0]
        if('LaunchTemplate' in required_info) :
            LaunchTemplate = required_info['LaunchTemplate']
            if('LaunchTemplateSpecification' in LaunchTemplate) :
                self.template_id = LaunchTemplate['LaunchTemplateSpecification']['LaunchTemplateId']
                self.template_name = LaunchTemplate['LaunchTemplateSpecification']['LaunchTemplateName']
            else:
                self.template_id = LaunchTemplate['LaunchTemplateId']
                self.template_name = LaunchTemplate['LaunchTemplateName']

        if ('MixedInstancesPolicy' in required_info) :
            self.template_id = response['AutoScalingGroups'][0]['MixedInstancesPolicy']['LaunchTemplate']['LaunchTemplateSpecification']['LaunchTemplateId']
            self.template_name = response['AutoScalingGroups'][0]['MixedInstancesPolicy']['LaunchTemplate']['LaunchTemplateSpecification']['LaunchTemplateName']    
            
        self.desired = response['AutoScalingGroups'][0]['DesiredCapacity']
        self.old_desired = self.desired
        self.mini = response['AutoScalingGroups'][0]['MinSize'] 
        self.old_mini = self.mini
        self.maxi = response['AutoScalingGroups'][0]['MaxSize']
        self.old_maxi = self.maxi
        self.list_of_old_instances , self.TargetGroupARNs = calc.asg_details(self.asg_name,self.desired,1)

    # def asg_details(self):
    #     asg_object = boto3.client('autoscaling')
    #     response = asg_object.describe_auto_scaling_groups(
    #         AutoScalingGroupNames=self.asg_name
    #     )    
    #     for i in range(self.desired):
    #         if(self.flag_for_asg_details == 0):
    #             self.list_of_old_instances.append(response['AutoScalingGroups'][0]['Instances'][i]['InstanceId'])
    #         else:
    #             self.list_of_old_instances.append(response['AutoScalingGroups'][0]['Instances'][i]['InstanceId'])
    #     TargetGroupARNs = response['AutoScalingGroups'][0]['TargetGroupARNs']
    #     self.flag_for_asg_details = 1

    def get_template(self):
        asg_launchtemplate = boto3.client('ec2') 
        response = asg_launchtemplate.describe_launch_templates(
            DryRun=False,
            LaunchTemplateIds=self.template_id
        )
        self.default_version = response['LaunchTemplates'][0]['DefaultVersionNumber']
        self.latest_version = response['LaunchTemplates'][0]['LatestVersionNumber']

    def template_version_details(self,image_id):
        asg_launchtemplate = boto3.client('ec2')
        response = asg_launchtemplate.describe_launch_template_versions(
            DryRun=False,
            LaunchTemplateId=self.template_id,
            Versions=str(self.default_version)
        )
        description = (response['LaunchTemplateVersions'][0]['VersionDescription'])
        self.new_version = utility.update_template_version(self.template_id,self.default_version,description,image_id)

    def set_protection(self):
        asg_object = boto3.client('autoscaling')
        asg_object.set_instance_protection(
            InstanceIds=self.list_of_old_instances,
            AutoScalingGroupName=self.asg_name, 
            ProtectedFromScaleIn=True
        )

    def asg_count_update(self):
        print("now executing asg_count_update methode : new version %s" %self.new_version)
        self.minimum_healthy_percentage = calc.calculate_minimum_healthy_percentage()
        if(self.desired > 2):
            for i in range(self.desired):
                scaling.scale_in_protection(self.asg_name,self.list_of_old_instances[i],False)
                updating.values(self.asg_name,self.template_name,self.new_version,self.minimum_healthy_percentage)
                self.list_of_new_instances = calc.asg_details(self.asg_name,self.desired)
                temp = list(set(self.list_of_new_instances) - set(self.list_of_old_instances))
                self.new_instance_after_refresh.append(temp[0])
                self.list_of_old_instances.append(self.new_instance_after_refresh[i])
                # in_tg = registerd.check_in_tg(self.TargetGroupARNs,self.new_instance_after_refresh[i])
                # if(in_tg is not True):    
                # else:
                new_box = health_check_utility.health_check(self.TargetGroupARNs,self.new_instance_after_refresh[i],self.asg_name,self.template_name,self.new_version,self.minimum_healthy_percentage,self.list_of_old_instances,self.desired,1)
                if(new_box != temp):
                    self.list_of_old_instances.append(new_box) 
                scaling.scale_in_protection(self.asg_name,self.new_instance_after_refresh[i],True)
        else:
            for i in range(self.desired):
                if(self.maxi == self.desired):
                    self.desired = self.desired + 1
                    self.maxi = self.maxi + 1
                elif(self.desired < self.maxi):
                    self.desired = self.desired + 1
                update_count.update_asg_count(self.asg_name,self.template_id,self.new_version,self.mini,self.maxi,self.desired)
                self.list_of_new_instances = calc.asg_details()
                temp = list(set(self.list_of_new_instances) - set(self.list_of_old_instances))
                self.new_instance_after_refresh.append(temp[0])
                new_box = health_check_utility.health_check(self.TargetGroupARNs,self.new_instance_after_refresh[i],self.asg_name,self.template_name,self.new_version,self.minimum_healthy_percentage,self.list_of_old_instances,1)
                if(new_box != temp[0]):
                   self.list_of_old_instances.append(new_box) 
                scaling.scale_in_protection(self.asg_name,self.new_instance_after_refresh,True)
            self.terminate_old_instance()

    def terminate_old_instance(self):
        scaling.scale_in_protection(self.asg_name,self.list_of_old_instances,False)
        update_count.update_asg_count(self.asg_name,self.template_id,self.new_version,self.old_mini,self.old_maxi,self.old_desired)

    def print_data(self):
        print("LaunchTemplate ID: %s \nLaunchTemplate Name: %s \nMin: %s \nMax: %s \nDesired: %s \nTargetGroupARNs: %s \nLaunchTemplate DefaultVersionNumber: %s \nLaunchTemplate LatestVersionNumber: %s \nDetails of Default LaunchTemplate: %s \nList of Instances In Asg: %s \n" % 
        (self.template_id,self.template_name,self.mini,self.maxi,self.desired,self.TargetGroupARNs,self.default_version,self.latest_version,self.default_version_details,self.list_of_instances))

if __name__ == "__main__" :
    obj = asg()
    name = input()
    image_id = input()
    obj.get_name(name)
    # obj.asg_details()
    obj.get_template()
    obj.template_version_details(image_id)
    obj.set_protection()
    obj.asg_count_update()
    # obj.asg_details()
    # obj.terminate_old_instance()
    obj.print_data()

#  lending-creditcard-consumer
#  ami_rollout_poc
#  ami-026dbd9b746f09d5f