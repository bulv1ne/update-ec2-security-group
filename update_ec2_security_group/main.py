from contextlib import contextmanager

import boto3
import inquirer
import requests
from botocore.exceptions import ClientError
from mypy_boto3_ec2 import EC2Client


def main():
    client = boto3.client("ec2")
    security_groups = {
        "{GroupId} - {GroupName}".format_map(sg): sg["GroupId"]
        for sg in client.describe_security_groups()["SecurityGroups"]
    }

    my_ip = requests.get("https://checkip.amazonaws.com").text.strip()

    answers = inquirer.prompt(
        [
            inquirer.List(
                "cidr_ip",
                "Select which IP address to allow SSH access from",
                choices=[f"{my_ip}/32", "0.0.0.0/0"],
            ),
            inquirer.List(
                "sg",
                message="Select a security group to update",
                choices=list(security_groups.keys()),
            ),
        ]
    )

    sg = answers["sg"]
    group_id = security_groups[sg]
    cidr_ip = answers["cidr_ip"]

    print(f"Updating security group: {sg}")
    with update_permissions(
        client,
        group_id,
        [
            {
                "IpProtocol": "tcp",
                "FromPort": 22,
                "ToPort": 22,
                "IpRanges": [{"CidrIp": cidr_ip}],
            },
        ],
    ):
        try:
            input("Press any key to continue...")
        except KeyboardInterrupt:
            pass


@contextmanager
def update_permissions(client: EC2Client, group_id, ip_permissions):
    try:
        try:
            client.authorize_security_group_ingress(
                GroupId=group_id,
                IpPermissions=ip_permissions,
            )
        except ClientError as e:
            if e.response["Error"]["Code"] == "InvalidPermission.Duplicate":
                print("Ingress rule already exists.")
            else:
                raise
        yield
    finally:
        client.revoke_security_group_ingress(
            GroupId=group_id,
            IpPermissions=ip_permissions,
        )


if __name__ == "__main__":
    main()
