import pandas as pd
import os, sys, stat, hashlib
from os.path import basename
import pandas as pd
import re
from androguard.core.bytecodes.apk import APK
from androguard.core.analysis.analysis import ExternalMethod
from androguard.misc import AnalyzeAPK
from androguard import *
from androguard.core.analysis import *
import argparse
import logging
import zipfile as zp
from termcolor import colored
import json
from constants import *

def parse_args(argv):
    parser = argparse.ArgumentParser(description='Extract APK Features.')
    parser.add_argument('--apk', dest='apk', required=True, help='Path to APK File to be Analysed')
    parser.add_argument('--logdir', dest='logdir', required=True, help='Path to Log Directory')
    parser.add_argument('--outdir', dest='outdir', required=True, help='Path to Building Queue')
    args = parser.parse_args(argv)
    return args

"""
implementação baseada na documentação
    https://github.com/androguard/androguard/issues/685
"""
def get_op_codes(dx):
    op_codes_dict = dict()
    #op_codes_list = list()
    for method in dx.get_methods():
        if method.is_external():
            continue
        m = method.get_method()
        for ins in m.get_instructions():
            ins_name = ins.get_name()
            ''' # discrete data
            if ins_name not in op_codes_list:
                op_codes_list.append(ins_name)
            '''
            # continous data
            if ins_name not in op_codes_dict:
                op_codes_dict[ins_name] = 1
            else:
                op_codes_dict[ins_name] += 1
    #return op_codes_list
    return op_codes_dict

def remove_apk(apk):
    #os.remove(apk)
    print(apk, 'Successfully Removed.')
    return

def get_intents(app):
    intents  = []
    services = app.get_services()
    serviceString = 'service'
    for service in services:
        for action, intent_name in app.get_intent_filters(serviceString, service).items():
            for intent in intent_name:
                intents.append(intent)

    receivers = app.get_receivers()
    receiverString = 'receiver'
    for receiver in receivers:
        for action,intent_name in app.get_intent_filters(receiverString, receiver).items():
            for intent in intent_name:
                intents.append(intent)

    activitys = app.get_activities()
    activityString = 'activity'
    for activity in activitys:
        for action,intent_name in app.get_intent_filters(activityString, activity).items():
            for intent in intent_name:
                intents.append(intent)

    intents = [i.split('.')[-1] for i in intents]
    return intents

def get_api_calls(cg):
    global sha256
    global args
    api_call_dict = dict()
    #api_call_list = list()
    common_methods = ['<init>', 'equals', 'hashCode', 'toString', 'clone', 'finalize', 'wait', 'print', 'println']
    # txt file to store the raw methods
    api_calls_file = os.path.join(args.outdir, f'{sha256}_all_api_calls.txt')
    with open(api_calls_file, 'w') as file:
        # iterate over CG containing the API Calls
        for node in cg.nodes:
            file.write(f'{str(node)}\n')
            _class = node.class_name
            method = node.name
            if is_android_api_call(node) and method not in common_methods:
                package = _class
                package = package.split("/")
                _class = package[-1]
                _class = _class[:-1]
                _class = _class.replace("$", ".")
                del package[-1]
                package = '.'.join(package)
                package_class = package + '.' + _class + '.' + method
                in_android_reference = (package in android_packages) and (_class in android_classes)
                ''' # discrete data
                if in_android_reference and package_class not in api_call_list:
                    api_call_list.append(package_class)
                '''
                #print(package_class)
                if in_android_reference:
                    if package_class not in api_call_dict:
                        api_call_dict[package_class] = 1
                    else:
                        api_call_dict[package_class] += 1

    # create zip file
    api_calls_zip = os.path.join(args.outdir, f'{sha256}_all_api_calls.zip')
    zip_file = zp.ZipFile(api_calls_zip, 'w', zp.ZIP_LZMA)
    zip_file.write(api_calls_file, basename(api_calls_file))
    zip_file.close()
    # remove txt
    os.remove(api_calls_file)
    #return api_call_list
    return api_call_dict

def is_android_api_call(class_method):
    if not isinstance(class_method, ExternalMethod):
        return False
    # Packages found at https://developer.android.com/reference/packages.html
    api_candidates = ["Landroid/", "Lcom/android/internal/util", "Ldalvik/", "Ljava/", "Ljavax/", "Lorg/apache/",
                      "Lorg/json/", "Lorg/w3c/dom/", "Lorg/xml/sax", "Lorg/xmlpull/v1/", "Ljunit/"]
    class_name = class_method.class_name
    for candidate in api_candidates:
        if class_name.startswith(candidate):
            return True
    return False

def info_warning_list(info):
    global logger
    i = colored(info, 'yellow')
    logger.warning(i)
    return list()

def save_as_json(data, output_name):
    with open(str(output_name), 'w') as fp:
        json.dump(data, fp, indent=4)

def extract_features(args):
    logging.basicConfig(format = '%(name)s - %(levelname)s - %(message)s')
    global logger
    global sha256
    logger = logging.getLogger('Extraction')
    try:
        f = open(args.apk, 'rb')
        contents = f.read()
    except e:
        info = colored(e, 'red')
        logger.exception(info)
        exit(1)

    sha256 = hashlib.sha256(contents).hexdigest()
    sha256 = sha256.upper()
    app, d, dx = AnalyzeAPK(args.apk)

    try:
        app_name = app.get_app_name()
    except:
        app_name = 'Not Found'
        info_warning_list('App Name Not Found')

    package = app.get_package()
    target_sdk = app.get_effective_target_sdk_version()
    min_sdk = app.get_min_sdk_version()
    try:
        permissions = app.get_permissions()
        permissions = [p.split('.')[-1] for p in permissions]
    except:
        permissions = info_warning_list('Could Not Extract Permissions')

    try:
        activities = app.get_activities()
    except:
        activities = info_warning_list('Could Not Extract Activities')

    try:
        services = app.get_services()
    except:
        services = info_warning_list('Could Not Extract Services')

    try:
        receivers = app.get_receivers()
    except:
        receivers = info_warning_list('Could Not Extract Receivers')

    try:
        providers = app.get_providers()
    except:
        providers = info_warning_list('Could Not Extract Providers')

    try:
        intents = get_intents(app)
    except:
        intents = info_warning_list('Could Not Extract Intents')

    try:
        op_codes = get_op_codes(dx)
    except:
        op_codes = info_warning_list('Could Not Extract OpCodes')

    try:
        cg = dx.get_call_graph()
        api_calls = get_api_calls(cg)
    except:
        api_calls = info_warning_list('Could Not Extract API Calls')

    data = [sha256, app_name, package, target_sdk, min_sdk, permissions, intents,
            activities, services, receivers, providers, op_codes, api_calls]

    extracted_features = ['SHA256', 'APP_NAME', 'PACKAGE', 'TARGET_API', 'MIN_API',
            'PERMISSIONS', 'INTENTS', 'ACTIVITIES', 'SERVICES', 'RECEIVERS',
            'PROVIDERS','OPCODES','APICALLS']
    # to .json
    json_data = dict()
    for i in range(len(extracted_features)):
        json_data[extracted_features[i]] = data[i]
    save_as_json(json_data, os.path.join(args.outdir, f'{sha256}.json'))
    ####

    # remover APK utilizado
    remove_apk(args.apk)

if __name__ == '__main__':
    global args
    args = parse_args(sys.argv[1:])
    extract_features(args)
