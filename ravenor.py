#!/usr/bin/env python3

import logging
import praw
import yaml
from pprint import pprint
from time import time, sleep

class Ravenor(object):
    """
    Implementation of main bot logic
    """
    def __init__(self, **kwargs):
        self.loglevel = 'info'
        self.log_format = '%(asctime)19s - %(levelname)8s - %(message)s'
        self.log_datefmt = '%d-%m-%Y %H:%M:%S'
        self.logmap = {
            'info': logging.INFO,
            'warning': logging.WARN,
            'warn': logging.WARN,
            'debug': logging.DEBUG
        }
        final_config = {**self.cmdargs(), **kwargs}
        for k in final_config:
            setattr(self, k, final_config[k])
        self._basic_logging()
        self.set_loglevel(self.loglevel)
        logging.debug('Load config file')
        self.config = self._load_yaml(self.config_file)
        self.database = self._load_yaml(self.config['database'])
        logging.info('Login to Reddit...')
        self.reddit = praw.Reddit(
            client_id=self.config['client_id'],
            client_secret=self.config['client_secret'],
            password=self.config['password'],
            user_agent='ravenor 0.0.1',
            username=self.config['username']
            )
        logging.info('Get target user...')
        self.target = self.reddit.redditor(self.config['target'])
        self.main_loop()

    def _basic_logging(self):
        logging.basicConfig(level=self.logmap[self.loglevel],
                            format=self.log_format,
                            datefmt=self.log_datefmt)

    def set_loglevel(self, level):
        logging.getLogger().setLevel(self.logmap[level])
        logging.debug('DEBUG mode is enabled')

    def _load_yaml(self, filename):
        with open(filename, 'r') as f:
            return(yaml.full_load(f))
        return None

    def cmdargs(self):
        description = 'Ravenor reddit bot'
        import argparse
        parser = argparse.ArgumentParser(
                description=description
                )

        parser.add_argument('--loglevel', '--log-level',
                            choices=self.logmap.keys(),
                            type=str.lower,
                            default=self.loglevel,
                            help='Logging level',
                            )
        parser.add_argument('--log-format',
                            type=str,
                            default=self.log_format,
                            help='Python Logger() compatible format string')
        parser.add_argument('--log-datefmt',
                            type=str,
                            default=self.log_datefmt,
                            help='Python Logger() compatible date format str')
        parser.add_argument('--config-file',
                            type=str,
                            default='/etc/ravenor/config.yml',
                            help='Path to config file (default /etc/ravenor/config.yml)')

        subparsers = parser.add_subparsers(dest='command')
        subparsers.required = False

        try:
            import argcomplete
            from os.path import basename
            parser.add_argument('--bash-completion',
                                action='store_true',
                                help='Dump bash completion file.'
                                ' Activate with eval '
                                '"$({} --bash-completion)"'.format(basename(__file__)))
            argcomplete.autocomplete(parser)
        except ModuleNotFoundError:
            pass

        args = parser.parse_args()
        if 'bash_completion' in args:
            if args.bash_completion:
                print(argcomplete.shellcode(basename(__file__), True, 'bash'))
        return vars(args)

    def main_loop(self):
        while True:
            self.handle = self.get_comments(
                self.config['target-sub'], time() - float(self.config['frequency']))
            for comment in self.handle:
                self.process(comment)
            self.handle = []
            logging.debug('Sleeping')
            sleep(int(self.config['frequency']))

    def get_comments(self, subreddit, since):
        logging.debug('Get comments')
        comments = self.target.stream.comments()
        valid = []
        for c in comments:
            logging.debug('Fetch comment')
            if c.created_utc >= since:
                logging.debug('New enough comment')
                if c.subreddit_name_prefixed == subreddit:
                    logging.debug('Correct subreddit')
                    valid.append(c)
            elif c.created < since:
                logging.debug('Comment too old, stop fetching')
                break
        return valid

    def process(self, comment):
        logging.info(comment.html_body)

if __name__ == '__main__':
    Ravenor()
