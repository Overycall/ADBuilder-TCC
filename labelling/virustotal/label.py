import argparse
import pandas as pd
import json
import os
from json.decoder import JSONDecodeError
#import shutil
import requests
import time
import datetime
import logging
from termcolor import cprint, colored
import subprocess
from spinner import Spinner


def parseArgs():
    parser = argparse.ArgumentParser(description='Dataset Labelling.')
    parser.add_argument('--sha256', metavar='SHA256', type=str, required = False, help='APK SHA256.')
    parser.add_argument('--vt_key', metavar='VT_KEY', type=str, required = True, help='VT API Key.')
    parser.add_argument('--outdir', metavar='OUTPUT_DIR', type=str, required = True, help='Path to Labelling Queue.')
    # parser.add_argument('--samples', metavar='SHA256_FILE', type=str, required = False, help='APKs SHA256 File')
    # parser.add_argument('--keys', metavar='VT_KEY_FILE', type=str, required = True, help='VT API Keys File')
    # parser.add_argument('--outdir', metavar='OUTPUT_DIR', type=str, required = True, help='Path to Labelling Queue')
    return parser.parse_args()

def handle_VT_error(args, response_json, endpoint):
    global logger
    error_dir = os.path.join(args.outdir, 'Errors')
    if 'error' in response_json:
        code = response_json['error']['code']
        message = response_json['error']['message']
        e = colored(f'{args.sha256} :: VT {code}: {message}', 'red')
        logger.error(e)
        error_dir = os.path.join(args.outdir, args.vt_key, f'{endpoint}_{code}')
    save_as_json(args.sha256, response_json, error_dir)

def handle_request_exception(e, type, args):
    global logger
    msg = colored(f'{type.capitalize()} Error: {e}', 'red')
    logger.exception(msg)
    error_dir = os.path.join(args.dir, 'Errors', type)
    if not os.path.exists(error_dir):
        os.makedirs(error_dir)
    file_path = os.path.join(error_dir, f'{args.sha256}.txt')
    with open(file_path, 'w') as f:
        f.write(msg)

def vt_request(sha256, vt_key):
    global logger
    url = f'https://www.virustotal.com/api/v3/files/{sha256}'
    try:
        response = requests.get(url, headers = {'x-apikey': vt_key})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as errh:
        handle_VT_error(args, response.json(), 'report')
    except requests.exceptions.ConnectionError as errc:
        handle_request_exception(errc, 'connection', args)
    except requests.exceptions.Timeout as errt:
        handle_request_exception(errt, 'timeout', args)
    except requests.exceptions.RequestException as err:
        handle_request_exception(err, 'request', args)
    except Exception as e:
        handle_request_exception(e, 'unknown', args)
    return None

def save_as_json(sha256, json_data, outdir):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    json_object = json.dumps(json_data, indent = 3)
    json_location = os.path.join(outdir, f'{sha256}.json')
    json_file = open(json_location, 'w')
    json_file.write(json_object)
    json_file.close()

def seconds_to_dhms(seconds):
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    print(f'{days}d {hours:02d}h {minutes:02d}m {seconds:02d}s')

def load_file(filename):
    with open(filename, 'r') as text_file:
        lines = text_file.readlines()
        lines = [line.rstrip('\n') for line in lines]
    return lines

if __name__=="__main__":
    logging.basicConfig(format = '%(name)s - %(levelname)s - %(message)s')
    global logger
    logger = logging.getLogger('Labelling')
    args = parseArgs()
    vt_key = args.vt_key
    sha256 = args.sha256
    # keys = load_file(args.vt_key)
    # samples = load_file(args.sha256)
    outdir = args.outdir

    print(f'Processing {sha256}. Key: {vt_key}')
    json_data = vt_request(sha256, vt_key)

    if json_data:
        try:
            last_analysis_date = int(json_data['data']['attributes']['last_analysis_date'])
            date = datetime.datetime.fromtimestamp(last_analysis_date)
            human_readable_date = date.strftime('%Y-%m-%d %H:%M:%S')  # format the date as desired
            print(f'Last Analysis: {human_readable_date}')
    
            app = json_data['data']['attributes']
            last_stats = app['last_analysis_stats']
            app_data = {'sha256': sha256,
                        'malicious': last_stats['malicious'],
                        'undetected': last_stats['undetected'],
                        'harmless': last_stats['harmless'],
                        'suspicious': last_stats['suspicious'],
                        'failure': last_stats['failure'],
                        'unsupported': last_stats['type-unsupported'],
                        'timeout': last_stats['timeout'],
                        'confirmed_timeout': last_stats['confirmed-timeout']}
            save_as_json(sha256, json_data, os.path.join(outdir, 'labeled'))
            labelling_data = pd.DataFrame([[app_data['sha256'],app_data['malicious'], last_analysis_date]], columns=['SHA256', 'MALICIOUS', 'LAST_ANALYSIS'])
            sha256_csv = os.path.join(outdir, 'labeled', f'{sha256}.csv')
            labelling_data.to_csv(sha256_csv, index = False)
            with open('log.txt', 'a') as f:
                f.write(f'{sha256}, {vt_key}\n')
        except JSONDecodeError as errd:
            e = colored(f'JSON Decoder Error: {errd}', 'red')
            logger.exception(e)
            save_as_json(sha256, json_data, os.path.join(outdir, 'Errors'))
        except TypeError as err:
            e = colored(f'JSON General Error: {err}', 'red')
            logger.exception(e)
            save_as_json(sha256, json_data, os.path.join(outdir, 'Errors'))

