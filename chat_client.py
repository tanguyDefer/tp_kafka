#!/usr/bin/env python3

import logging
import re
import sys
import threading

from kafka import KafkaConsumer, KafkaProducer

# Configuration du logger
log = logging.getLogger("chat_client")
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))

should_quit = False
SUB_CHANNELS = []


def read_messages(consumer):
    # TODO À compléter
    while not should_quit:
        # On utilise poll pour ne pas bloquer indéfiniment quand should_quit
        # devient True
        received = consumer.poll(100)

        for channel, messages in received.items():
            for msg in messages:
                print("< %s: %s" % (channel.topic, msg.value))



def cmd_msg(producer, channel, line):
    # TODO À compléter
    pass


def cmd_join(nick_name,consumer, producer, args):
    try:
        consumer.subscribe("chat_channel_" + args[1:])
        if args not in SUB_CHANNELS:
            SUB_CHANNELS.append(args)
        log.info("%s has joined chat channel %s",nick_name, args[1:])
        log.info("List of %s's channels : %s",nick_name, SUB_CHANNELS)
    except Exception as err:
        log.error("Subscribe to : %s failed", err)


def cmd_part(nick_name, consumer, producer, args):
    """function to quit a channel and join one of user's channels

    Args:
        consumer (_type_): kaka consumer
        producer (_type_): kafka producer
        args (_type_): channel to quit
    Returns:
        _type_: subscribe channel or False
    """
    if args in SUB_CHANNELS:
        if len(SUB_CHANNELS) < 1:
            log.warning("No channel subscribe")
            return None
        else:
            print("ARGS IN PART :" , args)
            consumer.unsubscribe()
            log.info("%s has left chat channel : %s",nick_name, args[1:])
            SUB_CHANNELS.remove(args)
            # TODO attention création d'un  new chan pas bon
            cmd_join(nick_name,consumer, producer, SUB_CHANNELS[-1])
            return True
    else:
        log.error("%s is not in your channels", args)
        return False

def cmd_quit(producer, line):
    # TODO À compléter
    pass

def channels_in_topic():
    """function to transform #general to chat_channel_general"""
    formated_channels = []
    for channel in SUB_CHANNELS:
        formated_channels.append("chat_channel_" + channel[1:])
    return formated_channels


def check_channel_format(args):
    """check if args format is correct
    Args:
        args (_type_): #general

    Returns:
        True or False
    """
    if re.match(r'^#[a-zA-Z0-9_-]+$', args):
        return True
    log.error("Incorrect channel format for '%s', channel format must be like '#general'", args)
    return False

def main_loop(nick_name, consumer, producer):
    curchan = None

    while True:
        try:
            if curchan is None:
                line = input("> ")
            else:
                line = input("[#%s]> " % curchan)
        except EOFError:
            log.error("/quit")
            line = "/quit"

        if line.startswith("/"):
            cmd, *args = line[1:].split(" ", maxsplit=1)
            cmd = cmd.lower()
            args = None if args == [] else args[0]
        else:
            cmd = "msg"
            args = line

        if not check_channel_format(args):
            continue
        else:
            if cmd == "msg":
                cmd_msg(producer, curchan, args)
            elif cmd == "join":
                if cmd_join(nick_name, consumer, producer, args):
                    curchan = args
            elif cmd == "part":
                return_value = cmd_part(nick_name,consumer, producer, args)
                if return_value or None:
                    curchan = SUB_CHANNELS[-1]
            elif cmd == "quit":
                cmd_quit(producer, args)
                break


def main():
    if len(sys.argv) != 2:
        print("usage: %s nick_name" % sys.argv[0])
        return 1

    nick_name = sys.argv[1]
    consumer = KafkaConsumer()
    producer = KafkaProducer()
    th = threading.Thread(target=read_messages, args=(consumer,))
    th.start()
    try:
        main_loop(nick_name, consumer, producer)
    finally:
        global should_quit
        should_quit = True
        th.join()



if __name__ == "__main__":
    sys.exit(main())
