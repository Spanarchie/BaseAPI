__author__ = 'colinmoore-hill'

import os

class BaseConfig(object):
    DEBUG = False
    SECRET_KEY = 'Magic-Moments'


class TestConfig(BaseConfig):
    DEBUG = True
    TESTING = True
    WTF_CSRF_ENABLED = False


class DevConfig(BaseConfig):
    DEBUG = True

class ProdConfig(BaseConfig):
    DEBUG = False

