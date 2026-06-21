import logging

def configure_logging(level = logging.INFO):
    logging.basicConfig(
        level=level,
        format='%(asctime)s.%(msecs)03d %(module)s: %(lineno)d %(levelname)-7s - %(message)s',
    )
    
