import boto3

# Create a session for user
# Provide aws_access_key_id and aws_secret_access_key
# this allows us to enter aws console

# aws_session = boto3.session(
#     aws_access_key_id = '',
#     aws_secret_access_key = ''
# )

aws_session = boto3.Session()

# to use resources invoke resources methode of a session and pass the service_name
# you wish to access
# this allows us to access s3 service after entering aws console

service_object = boto3.resource('s3')

# to print all s3 buckets run a for loop

for each_b in service_object.buckets.all():
    print(each_b.name)
