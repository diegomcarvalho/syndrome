import ray
import lmfit as lm

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
    
    def __init__(self):
        self.param_dict = dict()
        return

    def dump(self, filename):
        with open(filename, 'w') as f:
            keys = list(self.param_dict.keys())
            var_names = self.param_dict[keys[0]].var_names
            f.write('ct, success, chisqr, redchi, aic, bic, nfev, nvarys, ndata, nfree')
            for i in var_names:
                f.write(f', {i}')
            f.write('\n')
            for i in keys:
                success = self.param_dict[i].success
                chisqr = self.param_dict[i].chisqr
                redchi = self.param_dict[i].redchi
                aic = self.param_dict[i].aic
                bic = self.param_dict[i].bic
                nfev = self.param_dict[i].nfev
                nvarys = self.param_dict[i].nvarys
                ndata = self.param_dict[i].ndata
                nfree = self.param_dict[i].nfree
                f.write(f'{i}, {success}, {chisqr}, {redchi}, {aic}, {bic}, {nfev}, {nvarys}, {ndata}, {nfree}')
                for pm in var_names:
                    val = self.param_dict[i].params[pm].value
                    f.write(f', {val}')
                f.write('\n')
        return
    
    def set_param(self, key, tag, param):
        self.param_dict[key] = param
        with open(f'log/{key}-{tag}.json', 'w') as f:
            f.write(self.param_dict[key].params.dumps(cls=NpEncoder))
        return