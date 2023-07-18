#!/usr/bin/python3
import argparse
from dataclasses import asdict
import os
from pathlib import Path
import timeit
import time
import pandas as pd
import numpy as np
import sys
import shutil
from colorama import init
from termcolor import cprint, colored
from pyfiglet import figlet_format
import logging
from reprint import output

def parse_args(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument('--file', type=str, help='TXT file with a list of APKs SHA256.')
    parser.add_argument('--download', help='Download APK files.', action="store_true")
    parser.add_argument('--n_parallel_download', '-npd', type=int, default=1, help='Number of Parallel Process for Download.')
    parser.add_argument('--extraction', help='APK Feature Extraction.', action="store_true")
    parser.add_argument('--n_parallel_extraction', '-npe', type=int, default=1, help='Number of Parallel Process for Feature Extraction.')
    parser.add_argument('--labelling', help='Virus Total Labelling.', action="store_true")
    parser.add_argument('--vt_keys', type=str, help='TXT file with a VirusTotal\'s List of API Keys to Analysis.')
    parser.add_argument('--building', help='Building Dataset.', action="store_true")
    parser.add_argument('--delete', help='Delete All Previous Files.', action="store_true")

    args = parser.parse_args(argv)
    return args

def create_directories(_dirs):
    for _dir in _dirs.keys():
        Path(_dirs[_dir]).mkdir(parents=True, exist_ok=True)

def create_logs(_logs):
    create_directories(_logs)

def create_queues(_queues):
    create_directories(_queues)

def sufixes():
    from itertools import product
    l = list()
    s = 'abcdefghijklmnopqrstuvwxyz'
    p = product(*([s] * 2))
    for x, y in p:
        l.append(x + y)
    return l

def create_queues_files(queue, prefix, chunked_apk_list):
    global files_sufixes
    queue_directory = os.path.join('queues', queue)
    objects = os.listdir(queue_directory)
    for object in objects:
        if object.startswith(prefix):
            os.remove(os.path.join(queue_directory, object))

    for i in range(0, len(chunked_apk_list)):
        queue_file = os.path.join(queue_directory, f'{prefix}{files_sufixes[i]}')
        apk_list = chunked_apk_list[i]
        with open(queue_file, 'w') as f:
            f.write('\n'.join(apk_list))
            f.close()

def delete_files():
    objects = os.listdir('queues')
    for object in objects:
        shutil.rmtree(os.path.join('queues', object))
    objects = os.listdir('logs')
    for object in objects:
        shutil.rmtree(os.path.join('logs', object))

def count_files(directory, extension):
    if os.path.exists(directory):
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f)) and f.endswith(extension)]
        return len(files)
    else:
        return 0
'''
def print_info(info, in_color):
    if in_color:
        cprint(info, 'green', attrs = ['bold'])
    else:
        print(info)
'''

def print_info(info, in_color):
    if in_color:
        return colored(info, 'green', attrs = ['bold'])
    else:
        return info

def all_finished(execution_steps, queues):
    completed_steps = list()
    for step, selected in execution_steps.items():
        finished_file = f'{step}.finished'
        file_exists = os.path.exists(os.path.join(queues[step], finished_file))
        is_finished = not selected or (selected and file_exists)
        completed_steps.append(is_finished)
    return all(completed_steps)

#def main():
if __name__=="__main__":
    init(strip=not sys.stdout.isatty()) # strip colors if stdout is redirected
    logging.basicConfig(format = '%(name)s - %(levelname)s - %(message)s')
    global logger
    global files_sufixes
    logger = logging.getLogger('ADBuilder')
    files_sufixes = sufixes()
    os.system('clear')
    cprint(figlet_format('AD Builder!', font='starwars'), 'yellow', attrs=['bold', 'dark', 'blink'])

    args = parse_args(sys.argv[1:])

    if not args.file and (args.download or args.labelling):
        info = colored('The Following Arguments Are Required: --file', 'red')
        logger.error(info)
        exit(2)

    if not args.vt_keys and args.labelling:
        info = colored('The Following Arguments Are Required: --vt_keys', 'red')
        logger.error(info)
        exit(2)

    if args.delete:
        delete_files()

    queues = {'download': 'queues/download',
              'extraction': 'queues/extraction',
              'labelling': 'queues/labelling',
              'building': 'queues/building'}
    create_queues(queues)

    logs = {'download': 'logs/download',
            'extraction': 'logs/extraction',
            'labelling': 'logs/labelling',
            'building': 'logs/building'}
    create_logs(logs)

    execution_steps = {'download': args.download,
            'extraction': args.extraction,
            'labelling': args.labelling,
            'building': args.building}

    sha256_list = list()
    if args.file:
        try:
            with open(args.file) as file:
                lines = file.readlines()
                sha256_list = [(line[:-1]).upper() for line in lines]
                sha256_list = list(filter(len, sha256_list))
        except BaseException as e:
            info = colored(e, 'red')
            logger.exception(info)
            exit(2)

    sha256_number = len(sha256_list)
    extraction_count = sha256_number + count_files(os.path.join('queues', 'extraction'), '.downloaded')
    building_count = sha256_number + count_files(os.path.join('queues', 'building'), '.extracted')

    start_time = timeit.default_timer()
    if args.download:
        chunked_arrays = np.array_split(sha256_list, args.n_parallel_download)
        chunked_sha256_list = [list(array) for array in chunked_arrays]
        create_queues_files('download', 'queue_', chunked_sha256_list)
        os.system('./download/run_n_downloads.sh {} {} {} {} &'.format(
            args.n_parallel_download,
            queues['download'],
            queues['extraction'],
            logs['download']))

    if args.labelling:
        chunked_sha256_list = [sha256_list[i:i + 500] for i in range(0, len(sha256_list), 500)]
        create_queues_files('labelling', '500_VT_', chunked_sha256_list)

        os.system('./labelling/virustotal/run_n_labellings.sh {} {} {} {} &'.format(
            args.vt_keys,
            queues['labelling'],
            queues['building'],
            logs['labelling']))

    if args.extraction and extraction_count:
        os.system('./extraction/run_n_extractions.sh {} {} {} {} {} &'.format(
            args.n_parallel_extraction,
            queues['download'],
            queues['extraction'],
            queues['building'],
            logs['extraction']))

    if args.building and building_count:
        os.system('./building/run_building.sh {} {} {} {} &'.format(
            queues['labelling'],
            queues['extraction'],
            queues['building'],
            logs['building']))

    iteration_counter = 1
    finished = False
    with output(output_type = 'list', initial_len = 11) as output_lines:
        while not finished:
            output_lines[0] = colored(f'***** Execution Status {iteration_counter} *****', 'magenta', attrs=['bold'])
            #cprint(f'\n***** Execution Status {iteration_counter} *****', 'magenta', attrs=['bold'])
            output_lines[1] = colored(f'Elapsed Time: {timeit.default_timer() - start_time:.2f} Seconds', 'magenta', attrs=['bold'])
            #cprint(f'Elapsed Time: {timeit.default_timer() - start_time:.2f} Seconds', 'magenta', attrs=['bold'])
            if args.download:
                # download module information
                downloaded_count = count_files(os.path.join('queues', 'download', 'downloaded'), '.apk')
                info = f'Download: {downloaded_count}/{sha256_number}'
                output_lines[2] = print_info(info, downloaded_count == sha256_number)

            if args.extraction:
                # extraction module information
                extracted_count = count_files(os.path.join('queues', 'extraction', 'extracted'), '.json')
                info = f'Extraction: {extracted_count}/{extraction_count}'
                output_lines[3] = print_info(info, extracted_count == extraction_count)

            if args.labelling:
                # labelling module information
                labeled_count = count_files(os.path.join('queues', 'labelling', 'labeled'), '.csv')
                labeled_count += count_files(os.path.join('queues', 'labelling', 'Errors'), '.json')
                info = f'Labelling: {labeled_count}/{sha256_number}'
                output_lines[4] = print_info(info, labeled_count == sha256_number)

            if args.building:
                builded_count = count_files(os.path.join('queues', 'building', 'Clean'), '.added')
                info = f'Building: {builded_count}/{building_count}'
                output_lines[5] = print_info(info, builded_count == building_count)

                dir_dataset = "./queues/building/Final/ADBuilder_Dataset.csv"
                try:
                    if os.path.isfile(dir_dataset):
                        if os.path.getsize(dir_dataset) > 0:
                            df = pd.read_csv(dir_dataset)
                            output_lines[6] = '  '
                            output_lines[7] = '*** Dataset Under Construction ***'
                            output_lines[8] = f'Number of Samples: {len(df)}'
                            output_lines[9] = f'Number of Features: {len(df.columns)}'
                            output_lines[10] = f'Dataset Size: {os.path.getsize(dir_dataset)} bytes\n'
                except:
                    pass

            finished = all_finished(execution_steps, queues)
            iteration_counter += 1
            if not finished:
                time.sleep(5)

    end_time = timeit.default_timer()
    cprint(f'\n\n***** ADBuilder *****\nRun in {end_time - start_time:.2f} seconds.\n', 'green', attrs=['bold'])
