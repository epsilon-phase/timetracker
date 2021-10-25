"""
Provides an implementation of a configured property value, permitting storing changes, filters, etc

All values are stored in the top level of the json object, and then decoded using methods that may be associated with
them at runtime
"""
from typing import *
import json

from xdg import xdg_config_home


class ConfigTransform:
    __slots__ = ['input', 'output']
    input: Callable
    output: Callable

    def __init__(self, inp, output):
        self.input = inp
        self.output = output


def identity(obj):
    return obj


class ConfigStore:
    data: dict
    transformers: dict[str, ConfigTransform]

    def __init__(self, name):
        (xdg_config_home() / name).mkdir(parents=True, exist_ok=True)
        self.file = xdg_config_home() / name / "config.json"
        self.transformers = {}
        if not self.file.exists():
            self.file.touch(exist_ok=True)
            with self.file.open("w") as f:
                f.write("{}")
        with open(self.file, 'r') as f:
            try:
                self.data = json.load(f)
            except json.JSONDecodeError:
                print("Failed :/")
                self.data={}

    def get(self, key, default):
        if key in self.transformers.keys() and key in self.data.keys():
            return self.transformers[key].input(self.data[key])
        elif key in self.data.keys():
            return self.data[key]
        else:
            return default

    def set(self, key: str, value):

        if key in self.transformers.keys():
            self.data[key] = self.transformers[key].output(value)
        print(repr(self.data))
        with open(self.file, 'w') as f:
            try:
                s=json.dumps(self.data)
                f.write(s)
            except IOError:
                print("Fuck")

    def add_transform(self, name: str, input: Callable = identity, output: Callable = identity) -> None:
        self.transformers[name] = ConfigTransform(input, output)
