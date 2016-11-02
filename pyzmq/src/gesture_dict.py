'''
Created on 25 Oct 2016

@author: matthew
ordered dictionary describing hand gesture
'''
from collections import OrderedDict
import json

class GestureDict():
    def __init__(self):
        self.dict = OrderedDict()
        self.dict['pitch_min'] = 1
        self.dict['pitch_max'] = 2
        self.dict['roll_min'] = 1
        self.dict['roll_max'] = 2
        self.dict['duration_min'] = 1
        self.dict['duration_max'] = 2
        print('gesture_dict created')

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
            print('key {}, value {}'.format(key,value))
            self.dict[key] = value
            