import glob
from matplotlib.pyplot import axis
import pandas as pd
import os
import time
import argparse

def parseArgs():
    parser = argparse.ArgumentParser(description = 'Dataset Building.')
    parser.add_argument('--incsv', required = True, help = 'Extracted CSV File.')
    parser.add_argument('--inlabeled', required = True, help = 'Labelling CSV File.')
    parser.add_argument('--outdir', required = True, help = 'Path to Building Queue.')
    return parser.parse_args()

if __name__ == '__main__':
    args = parseArgs()
    if os.path.isfile(args.inlabeled):
        labeled = pd.read_csv(args.inlabeled)

    dataset_file = os.path.join(args.outdir, 'ADBuilder_Dataset.csv')
    if not os.path.exists(dataset_file):
        moto_df = pd.DataFrame()
    else:
        moto_df = pd.read_csv(dataset_file)

    features_csv = pd.read_csv(args.incsv)
    features_csv['LABELLING'] = labeled['MALICIOUS']
    dataset = pd.concat([moto_df, features_csv], ignore_index = True)
    dataset.fillna(0, inplace=True)
    for col in dataset:
        if dataset[col].dtype == 'float64':
            dataset[col] = dataset[col].astype(int)
    dataset.to_csv(dataset_file, index = False, encoding = 'utf-8-sig')
