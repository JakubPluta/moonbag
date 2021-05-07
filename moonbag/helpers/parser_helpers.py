import argparse
from typing import List
import logging
import os
from prompt_toolkit import PromptSession
from prompt_toolkit.eventloop.inputhook import set_eventloop_with_inputhook, InputHookContext
from prompt_toolkit.history import FileHistory, InMemoryHistory
import time

logger = logging.getLogger('parser')


rocketman = "(🚀🚀)"


class SessionMaker:
    _history = {
        'inmemory' : InMemoryHistory,
        'file' : FileHistory
    }

    history_file = os.path.join(os.path.expanduser("~"), ".moonbag.history")

    @classmethod
    def create_session(cls):
        session = PromptSession(history=FileHistory(cls.history_file))
        set_eventloop_with_inputhook(input_hook)
        return session


def parse_only_known_args(parser: argparse.ArgumentParser, args: List):
    (this_parser, others) = parser.parse_known_args(args)

    if others:
        logger.log(1, f"FOLLOWING ARGS WASN'T RECOGNIZED {others}")
    return this_parser


def input_hook(context: InputHookContext):
    while not context.input_is_ready():
        time.sleep(0.1)
    return False


try:
    session = SessionMaker.create_session()
except Exception as e:
    logger.log(1, 'COULD NOT CREATE SESSION: ', e)
    session = None


