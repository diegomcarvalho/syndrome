import ray
import lmfit as lm

import os
import json
import numpy as np

class NpEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.integer):
            return int(obj)
        elif isinstance(obj, np.floating):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        else:
            return super(NpEncoder, self).default(obj)

@ray.remote(num_cpus=0.1)
class ParamProcessor(object):
    
    def __init__(self, store):
        self.param_dict = dict()
        self.store = store
        return

    def dump(self, filename):
        with open(filename, 'w') as f:
            for tag in self.param_dict.keys():
                keys = list(self.param_dict[tag].keys())
                var_names = self.param_dict[tag][keys[0]].var_names
                f.write('tag, ct, success, chisqr, redchi, aic, bic, nfev, nvarys, ndata, nfree')
                for i in var_names.sort():
                    f.write(f', {i}')
                f.write('\n')
                for i in keys:
                    success = self.param_dict[tag][i].success
                    chisqr = self.param_dict[tag][i].chisqr
                    redchi = self.param_dict[tag][i].redchi
                    aic = self.param_dict[tag][i].aic
                    bic = self.param_dict[tag][i].bic
                    nfev = self.param_dict[tag][i].nfev
                    nvarys = self.param_dict[tag][i].nvarys
                    ndata = self.param_dict[tag][i].ndata
                    nfree = self.param_dict[tag][i].nfree
                    f.write(f'{tag}, {i}, {success}, {chisqr}, {redchi}, {aic}, {bic}, {nfev}, {nvarys}, {ndata}, {nfree}')
                    for pm in var_names.sort():
                        val = self.param_dict[tag][i].params[pm].value
                        f.write(f', {val}')
                    f.write('\n')
        return

    def get_param(self, key, tag):
        if tag in self.param_dict.keys():
            if key in self.param_dict[tag].keys():
                return self.param_dict[tag][key]
        params = lm.Parameters()

        try:
            with open(f'{self.store}/{tag}/{key}.json', 'r') as f:
                if tag not in self.param_dict.keys():
                    self.param_dict[tag] = dict()
                
                self.param_dict[tag][key] = params.load(f)
        except:
            return params

        return self.param_dict[tag][key]

    def set_param(self, key, tag, param):
        # Create a new dict if there isn't this tag
        if tag not in self.param_dict.keys():
            self.param_dict[tag] = dict()

        # Store the new param
        self.param_dict[tag][key] = param

        # Make a temporary copy onto the filesystem
        tmp_storage_directory = f'{self.store}/tmp/{tag}'
        if not os.path.exists(tmp_storage_directory):
            try:
                os.makedirs(tmp_storage_directory)
            except Exception as e:
                print(f'ParamProcessor: cannot create {tmp_storage_directory}')
                raise e

        with open(f'{self.store}/tmp/{tag}/{key}.json', 'w') as f:
            f.write(self.param_dict[tag][key].dumps(cls=NpEncoder))

        return