import boto3
import os
import tempfile
import random
import time
import uuid
import logging
import sys


def __keyFromEvent(event):
    return event['Records'][0]['s3']['object']['key']


def __bucketFromEvent(event):
    return event['Records'][0]['s3']['bucket']['name']


def downloadAndProcessFile(event):
    s3 = boto3.client('s3')
    BUCKET_INCOMING = os.environ['BUCKET_INCOMING']
    BUCKET_BADDATA = os.environ['BUCKET_BADDATA']
    BUCKET_PROCESSED = os.environ['BUCKET_PROCESSED']

    key = __keyFromEvent(event)
    bucket = __bucketFromEvent(event)

    with tempfile.TemporaryDirectory() as tmpdirname:
        logging.debug('created temporary directory %s', tmpdirname)
        key_base = os.path.basename(key)
        dest_filepath = os.path.join(tmpdirname, key_base)
        logging.debug('downloading %s to %s', key, dest_filepath)
        s3.download_file(bucket, key, dest_filepath)
        logging.debug('downloaded %s to %s', key, dest_filepath)

        # fail randomly 10% of the time
        if random.random() < 0.1:
            logging.debug('uploading %s to %s', key, dest_filepath)
            s3.upload_file(dest_filepath, BUCKET_BADDATA, key)
            logging.debug('uploaded %s to %s', key, dest_filepath)
            logging.error('sending FILE %s to s3://%s/%s',
                          dest_filepath, BUCKET_BADDATA, key)
            raise Exception('random failure')
        else:
            # "processing" the file by truncating it before sending to destination
            with open(dest_filepath, 'w+') as f:
                logging.debug('starting file processing')
                f.truncate(10)
                logging.debug('finished processing file')
                logging.debug('sending file %s to s3://%s/%s',
                              dest_filepath, BUCKET_PROCESSED, key)
                s3.upload_file(dest_filepath, BUCKET_PROCESSED, key)
                logging.info('sent file %s to s3://%s/%s',
                             dest_filepath, BUCKET_PROCESSED, key)


def createDbEntry(event):
    dynamodb = boto3.resource('dynamodb')
    TABLE_NAME = os.environ['TABLE_NAME']

    table = dynamodb.Table(TABLE_NAME)
    timestamp = int(time.time() * 1000)
    key = __keyFromEvent(event)
    bucket = __bucketFromEvent(event)

    logging.info('starting to create item in TABLE %s for s3://%s/%s',
                 TABLE_NAME, bucket, key)

    item = {
        'id': str(uuid.uuid4()),
        'bucket': bucket,
        'key': key,
        'processed': False,
        'createdAt': timestamp,
        'updatedAt': timestamp,
    }

    table.put_item(Item=item)
    logging.debug('finished putting item %s into %s', item, table)

    return item['id']


def updateDbEntry(itemId):
    dynamodb = boto3.resource('dynamodb')
    TABLE_NAME = os.environ['TABLE_NAME']

    table = dynamodb.Table(TABLE_NAME)
    timestamp = int(time.time() * 1000)

    logging.info('updating ITEM %s in TABLE %s', itemId, table)
    response = table.update_item(
        Key={
            'id': itemId
        },
        ExpressionAttributeNames={
            '#processed': 'processed',
            '#updatedAt': 'updatedAt',
        },
        ExpressionAttributeValues={
            ':processed': True,
            ':updatedAt': timestamp,
        },
        UpdateExpression='SET #processed = :processed, '
                         '#updatedAt = :updatedAt',
        ReturnValues='ALL_NEW',
    )
    logging.debug('finished updating item %s into %s', response, table)
