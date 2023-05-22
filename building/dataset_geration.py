import re
import pandas as pd
from pathlib import Path
import time
import json
import numpy as np
import os
import argparse
#from constants import *

def parseArgs():
    parser = argparse.ArgumentParser(description = 'Dataset Building.')
    parser.add_argument('--json', required = True, help = 'JSON File.')
    parser.add_argument('--outdir', required = True, help = 'Path to Building Queue.')
    return parser.parse_args()

if __name__ == '__main__':
    args = parseArgs()
    #start = time.time()

    # Opening JSON file
    json_file = open(args.json)
    json_data = json.load(json_file)
    json_file.close()

    discrete_extracted_features = ['PERMISSIONS', 'INTENTS']
    continuous_extracted_features =  ['OPCODES', 'APICALLS']

    feature_prefix = {
        'PERMISSIONS': 'Permission',
        'INTENTS': 'Intent',
        'OPCODES': 'OpCode',
        'APICALLS': 'API Call'
    }
    features = list()
    for eft in discrete_extracted_features:
        feature_list = json_data[eft]
        prefix = feature_prefix[eft]
        for feature in feature_list:
            features.append(f'{prefix} :: {feature}')

    lst = [1] * len(features)
    #df_features = pd.DataFrame([lst], columns = features)

    for eft in continuous_extracted_features:
        if not json_data[eft]:
            continue
        feature_list = list(json_data[eft].keys())
        prefix = feature_prefix[eft]
        for feature in feature_list:
            features.append(f'{prefix} :: {feature}')
        values_list = list(json_data[eft].values())
        lst.extend(values_list)

    df_features = pd.DataFrame([lst], columns = features)

    extracted_metadata = ['SHA256', 'APP_NAME', 'PACKAGE', 'TARGET_API', 'MIN_API']
    metadata = list()
    for em in extracted_metadata:
        metadata.append(json_data[em])
    df_metadata = pd.DataFrame([metadata], columns = extracted_metadata)

    df = df_metadata.join(df_features)

    sha256 = json_data['SHA256']
    csv_file = os.path.join(args.outdir, f'{sha256}.csv')
    df.to_csv(csv_file, index = False)

    #end = time.time()
