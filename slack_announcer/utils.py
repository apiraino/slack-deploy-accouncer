import boto3


def get_ssm_client():
    return boto3.client('ssm')


def get_slack_key(key):
    ssm_client = get_ssm_client()
    response = ssm_client.get_parameter(
        Name='/slack_deployer/{}'.format(key),
        WithDecryption=True
    )
    return response['Parameter']['Value']
