# Processing objects from S3 Events with Lambda function

## Structure

`handler.py` is the entrypoint which drives the behavior of the `processor.py` module.

## Use Cases

This project could be used as a template to receive files on a given bucket. Files that are successfully processed are copied to a "processed" bucket, while errored files go to the "bad data" bucket. Object keys may need to be rewritten in order to avoid collisions and overwriting.

## Setup

1. `virtualenv -p python3 env`, `source env/bin/activate`, and `pip install boto3` to get your local environment ready. The AWS Lambda runtime already includes Boto3
2. Make sure you name the service that's likely to be globally unique. S3 bucket names are derived from the service name
3. Customize the `processor.py` to how you want to process the incoming files. Two output buckets are available for processed data and errored data. Optionally keep a record of objects with DynamoDB.

## Deploy

1. `sls deploy`!
2. Check the CloudFormation outputs to find the name of the bucket that accepts incoming files.

## Scaling

### AWS Lambda

By default, AWS Lambda limits the total concurrent executions across all functions within a given region to 100. The default limit is a safety limit that protects you from costs due to potential runaway or recursive functions during initial development and testing. To increase this limit above the default, follow the steps in [To request a limit increase for concurrent executions](http://docs.aws.amazon.com/lambda/latest/dg/concurrent-executions.html#increase-concurrent-executions-limit).

### DynamoDB

When you create a table, you specify how much provisioned throughput capacity you want to reserve for reads and writes. DynamoDB will reserve the necessary resources to meet your throughput needs while ensuring consistent, low-latency performance. You can change the provisioned throughput and increasing or decreasing capacity as needed.

This is can be done via settings in the `serverless.yml`.

```yaml
  ProvisionedThroughput:
    ReadCapacityUnits: 1
    WriteCapacityUnits: 1
```
