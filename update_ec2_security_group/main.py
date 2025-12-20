from pprint import pprint

import boto3
from botocore.exceptions import ClientError


def main():
    client = boto3.client("ec2")
    for sg in client.describe_security_groups()["SecurityGroups"]:
        if sg["GroupName"] == "sleipnir-server":
            print(f"Updating security group: {sg['GroupName']}")
            try:
                client.authorize_security_group_ingress(
                    GroupId=sg["GroupId"],
                    IpPermissions=[
                        {
                            "IpProtocol": "tcp",
                            "FromPort": 22,
                            "ToPort": 22,
                            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                        },
                    ],
                )
            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidPermission.Duplicate':
                    print("Ingress rule already exists.")
                else:
                    raise
            try:
                input("Press any key to continue...")
            finally:
                client.revoke_security_group_ingress(
                    GroupId=sg["GroupId"],
                    IpPermissions=[
                        {
                            "IpProtocol": "tcp",
                            "FromPort": 22,
                            "ToPort": 22,
                            "IpRanges": [{"CidrIp": "0.0.0.0/0"}],
                        }
                    ]
                )


if __name__ == "__main__":
    main()
