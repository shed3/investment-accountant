import json
import os
from decimal import Decimal


class Fixes:

    def local_txs(file_path=''):
        file = file_path if file_path else os.path.dirname(os.path.realpath(__file__))"/example_txs.json"
        print(file)
        with open(file, 'r') as json_file:
            all_trans = json.load(json_file)
            for trans in all_trans:
                for key in trans:
                    val = trans[key]
                    if isinstance(val, int) or isinstance(val, float):
                        val = Decimal(str(val))
                    trans[key] = val
        return sorted(all_trans, key=lambda x: x['timestamp'])
