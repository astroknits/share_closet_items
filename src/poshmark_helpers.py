import time
from random import randint

class PoshmarkHelpers:
    @staticmethod
    def add_jitter(value):
        sigma = 1
        value = int(value)
        return randint(value - sigma, value + sigma)

    @staticmethod
    def sleep(value):
        time.sleep(PoshmarkHelpers.add_jitter(value))

