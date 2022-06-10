#!/usr/bin/env python3

import re
import sys
import threading
import logging

from kafka import KafkaProducer, KafkaConsumer

# Configuration du logger
log = logging.getLogger("chat_client")
log.setLevel(logging.INFO)
log.addHandler(logging.StreamHandler(sys.stdout))
should_quit = False


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


def cmd_join(consumer, producer, args):
    try:
        re.match(r'^#[a-zA-Z0-9_-]+$', args)
        consumer.subscribe("chat_channel_" + args[1:])
        log.info("Subscribed to : %s", args[1:])
        return True
    except Exception as err:
        log.error("ERROR: %s", err)
        return False


def cmd_part(consumer, producer, line):
    # TODO À compléter
    pass


def cmd_quit(producer, line):
    # TODO À compléter
    pass


def main_loop(nick, consumer, producer):
    curchan = None

    while True:
        try:
            if curchan is None:
                line = input("> ")
            else:
                line = input("[#%s]> " % curchan)
        except EOFError:
            print("/quit")
            line = "/quit"

        if line.startswith("/"):
            cmd, *args = line[1:].split(" ", maxsplit=1)
            cmd = cmd.lower()
            args = None if args == [] else args[0]
        else:
            cmd = "msg"
            args = line

        if cmd == "msg":
            cmd_msg(producer, curchan, args)
        elif cmd == "join":
            if cmd_join(consumer, producer, args):
                curchan = args
        elif cmd == "part":
            cmd_part(consumer, producer, args)
        elif cmd == "quit":
            cmd_quit(producer, args)
            break
        # TODO: rajouter des commandes ici


def main():
    if len(sys.argv) != 2:
        print("usage: %s nick" % sys.argv[0])
        return 1

    nick = sys.argv[1]
    consumer = KafkaConsumer()
    producer = KafkaProducer()
    th = threading.Thread(target=read_messages, args=(consumer,))
    th.start()
    try:
        main_loop(nick, consumer, producer)
    finally:
        global should_quit
        should_quit = True
        th.join()



if __name__ == "__main__":
    sys.exit(main())
