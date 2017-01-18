'''
Created on 25 Oct 2016

@author: matthew
ordered dictionary describing hand gesture
'''
from collections import OrderedDict
import logging
import json

class GestureDict():
    def __init__(self):
        self.dict = OrderedDict()
        self.dict['magnitude_min'] = 20
        self.dict['magnitude_max'] = 30
        self.dict['filter_length'] = 100
        self.dict['events'] = 1
        logging.basicConfig(level=logging.DEBUG, format='%(message)s')
        logging.info('gesture_dict created')

    def get_dict(self):
        return self.dict
    
    def load_json(self, json_obj):
        ''' return the python data structure '''
        return json.loads(json)
    
    def make_json(self):
        ''' return the json form of self.dict '''
        return json.dumps(self.dict)
    
    def hello(self):
        print('hello from gesture_dict')
    
    def update_dict(self, **kwargs):
        ''' update dict with kwargs '''
        for key, value in kwargs.items():
            logging.info('key {}, value {}'.format(key,value))
            self.dict[key] = value
            