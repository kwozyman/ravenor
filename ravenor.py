#!/usr/bin/env python3

import praw
import yaml
from pprint import pprint
from time import time, sleep

class Ravenor(object):
    def __init__(self, config_file):
        self.config = self._load_yaml(config_file)
        self.database = self._load_yaml(self.config['database'])
        self.reddit = praw.Reddit(
            client_id=self.config['client_id'],
            client_secret=self.config['client_secret'],
            password=self.config['password'],
            user_agent='ravenor 0.0.1',
            username=self.config['username']
            )
        self.target = self.reddit.redditor(self.config['target'])
        self.main_loop()

    def _load_yaml(self, filename):
        with open(filename, 'r') as f:
            return(yaml.full_load(f))
        return None

    def main_loop(self):
        while True:
            self.handle = self.get_comments(config['target-sub'], time() - float(config['frequency']))
            for comment in self.handle:
                self.process(comment)
            self.handle = []
            sleep(int(config['frequency']))

    def get_comments(self, subreddit, since):
        comments = self.target.stream.comments()
        valid = []
        for c in comments:
            if c.created_utc >= since:
                if c.subreddit_name_prefixed == subreddit:
                    valid.append(c)
            elif c.created < since:
                break
        return retaliate

    def process(self, comment):
        print(comment.html_body)
