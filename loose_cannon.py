#!/usr/bin/env python3.11

import boto3
import argparse
import os
import time

def terminate_instances(ec2_client, instance_ids):
    try:
        response = ec2_client.terminate_instances(InstanceIds=instance_ids)
        return response
    except Exception as e:
        print("Error terminating instances:", e)
        return None

def main():
    parser = argparse.ArgumentParser(description="Loose Cannon - Simulate chaos by terminating EC2 instances")
    parser.add_argument("--instance-id", help="Specific instance ID to terminate")
    parser.add_argument("--instance-ids", nargs="+", help="List of instance IDs to terminate")
    args = parser.parse_args()

    # Read AWS credentials from ~/.aws/credentials file
    aws_credentials = {}
    credentials_file = os.path.expanduser("~/.aws/credentials")
    if os.path.exists(credentials_file):
        with open(credentials_file, "r") as f:
            for line in f:
                if line.strip().startswith("[") or not line.strip():
                    continue
                key, value = line.strip().split("=", 1)
                aws_credentials[key.strip()] = value.strip()

    if not aws_credentials:
        print("AWS credentials not found in ~/.aws/credentials file.")
        return

    if not args.instance_id and not args.instance_ids:
        print("Please provide either --instance-id or --instance-ids parameter.")
        return

    ec2_client = boto3.Session(
        aws_access_key_id=aws_credentials.get("aws_access_key_id"),
        aws_secret_access_key=aws_credentials.get("aws_secret_access_key"),
    ).client("ec2")

    try:
        if args.instance_id:
            instances_to_terminate = [args.instance_id]
        else:
            instances_to_terminate = args.instance_ids

        print("Terminating instances:", instances_to_terminate)
        termination_result = terminate_instances(ec2_client, instances_to_terminate)
        if termination_result:
            # Wait for termination to complete
            waiter = ec2_client.get_waiter('instance_terminated')
            waiter.wait(InstanceIds=instances_to_terminate)
            print("Termination completed.")

            # Create logs directory if not exists
            logs_dir = os.path.join(os.getcwd(), "logs")
            if not os.path.exists(logs_dir):
                os.makedirs(logs_dir)

            # Write results to log file
            timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
            log_file = os.path.join(logs_dir, f"{timestamp}.log")
            with open(log_file, "w") as f:
                f.write("Termination results:\n")
                f.write(str(termination_result))
            print(f"Termination results saved to {log_file}")

            exit(0)
        else:
            exit(1)
    except Exception as e:
        print("Error:", e)
        exit(1)

if __name__ == "__main__":
    main()
