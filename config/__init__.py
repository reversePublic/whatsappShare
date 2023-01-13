import logging

logger = logging.getLogger(__name__)
ch = logging.StreamHandler()
# ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(levelname).1s %(asctime)s %(name)s - %(message)s')

ch.setFormatter(formatter)

logger.addHandler(ch)