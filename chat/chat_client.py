#!/usr/bin/env python3

import logging
import re
from socket import timeout
import sys
import threading

import coloredlogs
from kafka import KafkaConsumer, KafkaProducer

should_quit = False
SUB_CHANNELS = []



# Configuration du logger
log = logging.getLogger("chat_client")
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))

"""pour le logger en local"""
coloredlogs.install(
    fmt="[%(asctime)s] %(levelname)s | %(message)s",
    level_styles={
        "info": {"color": "green"},
        "notice": {"color": "magenta"},
        "verbose": {"color": "green"},
        "success": {"color": "green", "bold": True},
        "spam": {"color": "cyan"},
        "critical": {"color": "red", "bold": True},
        "error": {"color": "red"},
        "debug": {"color": "blue"},
        "warning": {"color": "yellow"},
    },
    logger=log,
    field_styles={
        "asctime": {"color": "white"},
        "levelname": {"color": "black", "bold": True},
    },
    level="info",
)


def read_messages(consumer):
    # TODO À compléter
    while not should_quit:
        # On utilise poll pour ne pas bloquer indéfiniment quand should_quit
        # devient True
        received = consumer.poll(100)

        for channel, messages in received.items():
            for msg in messages:
                print("< %s: %s" % (channel.topic, msg.value))



def cmd_msg(consumer, producer, curchan, args, nick_name):
    if curchan:
            log.info("Sending message to %s ...", curchan)
            formated_curchan = "chat_channel_" + curchan[1:]
            message = nick_name + ": " + args
            try:
                producer.send(formated_curchan, str.encode(message)).get(timeout=5)
                producer.flush()
                log.info("Message sent by %s on channel %s", nick_name, curchan)
            except Exception as err:
                log.warning("Impossible to send message ... %s", err)
    else:
        log.warning("No active channel")


def cmd_join(nick_name,consumer, producer, args):
    try:
        consumer.subscribe("chat_channel_" + args[1:])
        if args not in SUB_CHANNELS:
            SUB_CHANNELS.append(args)
        log.info("%s has joined chat channel %s",nick_name, args[1:])
        log.info("List of %s's channels : %s",nick_name, SUB_CHANNELS)
        return True
    except Exception as err:
        log.error("Subscribe to : %s failed", err)
        return False


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
        if len(SUB_CHANNELS) == 0:
            log.warning("No channel subscribe")
        else:
            if len(SUB_CHANNELS) == 1:
                log.warning("You will not subscribe to any channels ... redirect to channels list")
                consumer.unsubscribe()
                log.info("%s has left chat channel : %s",nick_name, args[1:])
                SUB_CHANNELS.remove(args)
                main()
            consumer.unsubscribe()
            log.info("%s has left chat channel : %s",nick_name, args[1:])
            SUB_CHANNELS.remove(args)
            cmd_join(nick_name,consumer, producer, SUB_CHANNELS[-1])
    else:
        log.warning("%s is not in your channels", args)
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

        if cmd == "msg":
            cmd_msg(consumer, producer, curchan, args, nick_name)
        elif cmd == "join":
            if check_channel_format(args) and cmd_join(nick_name, consumer, producer, args):
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
        log.warning("usage: %s nick_name" % sys.argv[0])
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
