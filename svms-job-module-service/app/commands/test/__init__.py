#!/usr/bin/env python
from moaiohttp.library.commands import BaseCommand

class Command(BaseCommand):
    def handle(self, *args):
        print("Success: This is a test command")