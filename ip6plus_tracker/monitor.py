from copy import deepcopy
from datetime import datetime
from httplib import HTTPConnection
from itertools import izip
from json import loads
from os import system
from time import sleep
from urllib import quote_plus

from models import nice_model_name


def start_monitoring(zip_code, target_stores, alert_models, beep_models):
    from ip6plus_tracker import HOST

    path = get_path(zip_code, alert_models + beep_models)
    first_time = True

    last_results = None

    while True:

        print '\nchecking status at %s' % datetime.now().strftime('%X %a %b %d')

        connection = HTTPConnection(HOST)
        connection.request("GET", path, headers={"Cache-Control" : "no-cache"})
        stores = loads(connection.getresponse().read())['body']['stores']

        results = [{'store': store['storeName'], 'models':
                      [model for model, info in store['partsAvailability'].items() if info['pickupDisplay'] == 'available']}
                   for store in stores if store['storeName'] in target_stores]

        alert = False
        beep = False

        for result in results:
            if not result['models']:
                if first_time:
                    print '-- %s has no stock of any of the tracked models (will only print once until stock returns)' % result['store']
            else:

                alerts = []
                beeps = []
                for model in result['models']:
                    alerts.append(model) if model in alert_models else beeps.append(model)

                if alerts and beeps:
                    alert = True
                    print '\n>>>>>>>>>>>>>>>'
                    print '-- %s HAS %s IN STOCK! It also has %s.' % (result['store'].upper(), pretty_list(alerts),
                                                                      pretty_list(beeps))
                    print '>>>>>>>>>>>>>>>\n'

                elif alerts:
                    alert = True
                    print '\n>>>>>>>>>>>>>>>'
                    print '%s HAS %s IN STOCK!' % (result['store'].upper(), pretty_list(alerts))
                    print '>>>>>>>>>>>>>>>\n'

                elif beeps:
                    beep = True
                    print '-- %s has %s in stock.' % (result['store'], pretty_list(beeps))


        if alert:
            system('afplay song.m4a')
        elif beep and last_results != results:
            print '\a\a\a\a\a'

        last_results = deepcopy(results)

        if first_time:
            first_time = False
        sleep(30)

def get_path(zip_code, models):
    from ip6plus_tracker import PATH_ROOT

    path = PATH_ROOT + zip_code

    for model, index in izip(models, range(len(models))):
        path += '&parts.{index}={model}'.format(index=index, model=quote_plus(model))

    return path

def pretty_list(models):
    if len(models) == 1:
        return str(nice_model_name(models[0]))
    if len(models) == 2:
        return '%s and %s' % (nice_model_name(models[0]), nice_model_name(models[1]))
    else:
        nice_str = ''
        for model in models[:-1]:
            nice_str += '%s, ' % nice_model_name(model)
        return nice_str + 'and %s' % nice_model_name(model[-1])