import logging
import sys

import processor

LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def gather(event, context):
    logging.info('starting gather')
    logger.debug(event)


def process(event, context):

    logging.basicConfig(format=LOG_FORMAT, stream=sys.stdout)

    logging.info('starting event processing')
    logging.debug(event)

    itemId = processor.createDbEntry(event)
    processor.downloadAndProcessFile(event)
    processor.updateDbEntry(itemId)

    return
