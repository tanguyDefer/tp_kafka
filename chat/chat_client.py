#!/usr/bin/env python3

import logging
import re
import sys
import threading

import coloredlogs
from kafka import KafkaConsumer, KafkaProducer

should_quit = False
SUB_CHANNELS = []
BOT_CHANNEL = "chat_channel_bot"


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


def cmd_msg(producer, curchan, message, nick_name):
    if curchan:
        log.info("Sending message to %s ...", curchan)
        formated_curchan = "chat_channel_" + curchan[1:]
        formated_message = str.encode(nick_name + ": " + message)
        try:
            # Kafka attend un message format bytes, il faut donc convertir avec str.encode()
            producer.send(formated_curchan, formated_message)
            producer.send(BOT_CHANNEL, key=str.encode(nick_name), value=formated_message)
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
        message_to_channel = "{} has joined chat channel : {} ".format(nick_name, args[1:])
        log.info(message_to_channel)
        info_message_to_channel(producer, args, message_to_channel)
        log.info("List of %s's channels : %s",nick_name, SUB_CHANNELS)
        return True
    except Exception as err:
        log.error("Subscribe to : %s failed", err)
        return False

def is_active(args):
    """Permet d'activer un canal et recevoir les messages sur ce canal

    Args:
        args (str): channel name
    """
    if args in SUB_CHANNELS:
        log.info("Channel : {} is now active".format(args))
        return True
    else:
        log.warning("Channel {} is not in your channel list : {}".format(args, SUB_CHANNELS))
        return False

def cmd_part(nick_name, consumer, producer, args):
    """function to quit a channel and join one of user's channels

    Args:
        consumer (kaka consumer)
        producer (kaka producer)
        args (str): channel to quit
    Returns:
        _type_: subscribe channel or False
    """
    if args in SUB_CHANNELS:
        if len(SUB_CHANNELS) == 0:
            log.warning("No channel subscribe")
        else:
            if len(SUB_CHANNELS) == 1:
                log.warning("You will not subscribe to any channels ... redirect to channels list")
                message_to_channel = "{} has left chat channel : {} ".format(nick_name, args[1:])
                log.info(message_to_channel)
                info_message_to_channel(producer, args, message_to_channel)
                consumer.unsubscribe()
                SUB_CHANNELS.remove(args)
                return True
            consumer.unsubscribe()
            log.info("%s has left chat channel : %s",nick_name, args[1:])
            message_to_channel = "{} has left chat channel : {} ".format(nick_name, args[1:])
            info_message_to_channel(producer, args, message_to_channel)
            consumer.unsubscribe()
            SUB_CHANNELS.remove(args)
            log.warning(consumer)
            # is_active(nick_name,consumer, producer, SUB_CHANNELS[-1])
            return True
    else:
        log.warning("%s is not in your channels", args)
        return False


def cmd_quit(producer, nick_name):
    message_to_channel = "{} has disconnected".format(nick_name)
    for channel in SUB_CHANNELS:
        info_message_to_channel(producer, channel, message_to_channel)
        log.info("Disconnected")


def info_message_to_channel(producer, args, message_to_channel):
    formated_channel = format_channel_name(args)
    producer.send(formated_channel, str.encode(message_to_channel))


def format_channel_name(args):
    """function to transform #general to chat_channel_general"""
    return "chat_channel_" + args[1:]


def check_channel_format(args):
    """check if args format is correct
    Args:
        args (_type_): #general

    Returns:
        True or False
    """
    if re.match(r'^#[a-zA-Z0-9_-]+$', args):
        return True
    log.warning("Incorrect channel format for '%s', channel format must be like '#general'", args)
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
            cmd_msg(producer, curchan, args, nick_name)
        elif cmd == "join":
            if check_channel_format(args):
                cmd_join(nick_name, consumer, producer, args)
                curchan = args
        elif cmd == "active":
            if is_active(args):
                curchan = args
        elif cmd == "part":
            return_value = cmd_part(nick_name,consumer, producer, args)
            if return_value or None:
                curchan = SUB_CHANNELS[-1]
        elif cmd == "quit":
            cmd_quit(producer, nick_name)
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
    try:
        sys.exit(main())
    except Exception as err:
        log.error("Unknown error : %s",err)
