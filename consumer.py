# -*- coding: utf-8 -*-
# @Time    : 2020/12/5 上午9:26
# @Author  : zhangqingfeng
# @FileName: receiver.py
# @Software: IntelliJ IDEA
# @Cnblogs ：https://blog.csdn.net/weixin_42051109

import gnsq
import json
import time
import threading
import requests
from random import randint
from stem.control import Controller
import os
import socket

NSQ_HOST = "108.61.250.38:4150"
NSQ_TOPIC = "task12"
NSQ_CONSUMER_CHANNEL = socket.gethostname()
consumer = gnsq.Consumer(NSQ_TOPIC, NSQ_CONSUMER_CHANNEL, NSQ_HOST,max_tries=1)
FINGERPRINT = ["85359D7950AC7906E66A2E7D4515C90A2DB73CA7","91F5F66C82F93546C1E8D1C5D30BE9B446F7A1D0"]

@consumer.on_message.connect
def handler(consumer, message):
    '''
    accept the command that build a node or delete it.
    :param consumer:
    :param message:
    :return:
    '''
    onion_address_id_list = json.loads(message.body.decode())["task_list"]
    print("message is:",type(onion_address_id_list),onion_address_id_list)
    process_function(onion_address_id_list)

def process_function(onion_address_id_list):
    start_tor()
    onion_address_list = []
    with Controller.from_port(port=9051) as controller:
        controller.authenticate()
        for item1 in FINGERPRINT:
            controller.msg("TRANSMITRPFINGERPRINT {}".format(item1))
            time.sleep(1)
        for item in onion_address_id_list:
            onion_address,onion_id = item
            temporary_onion_address= "http://" + onion_address + ".onion"
            onion_address_list.append(temporary_onion_address)

            controller.msg("TRANSMITONIONID {} {}".format(onion_address, onion_id))
            time.sleep(1)
    threads_list = create_threding(onion_address_list)

    start_threading(threads_list)
    for item_threading in threads_list:
        item_threading.join()

    kill_tor()


def start_tor():
    '''
    starting the tor app.
    :return:
    '''
    os.system("/home/torProject/tor-tor-0.4.4.6/src/app/tor -f /home/torProject/torrc")
    time.sleep(5)


def kill_tor():
    '''
    killing the tor app.
    :return:
    '''
    os.system("killall tor")
    os.system("rm -rf /home/torProject/data/")
    time.sleep(5)
    os.system("killall curl")


def create_threding(onion_address_list):
    '''
    creating the list of thread whose number is decided by the length of onion_list.
    :return:
    '''
    return [threading.Thread(target=visit_onion_web, args=(onion_address,)) for onion_address in onion_address_list]


def start_threading(threading_list):
    '''
    staring every thread.
    :param threading_list:
    :return:
    '''
    for item_threading in threading_list:
        item_threading.start()

    #for item_threading in threading_list:
        #item_threading.join()
        pass
   # kill_tor()

def visit_onion_web(onion_address):
    '''
    visiting the onion website by request lib.
    :param onion_address:
    :return:
    '''
    proxies = {'http': 'socks5h://127.0.0.1:9150', 'https': 'socks5h://127.0.0.1:9150'}
    s = requests.session()
    try:
        response = s.get(onion_address, proxies=proxies,timeout=20)
        print(response.text)
        print("---------",threading.current_thread().getName(),"---------onion_address is: ",onion_address)
    except requests.exceptions.ConnectionError as e:
        print("Error is: ", e)
    except requests.exceptions.RequestException as e:
        print("Error is: ", e)


if __name__ == "__main__":
    consumer.start()
