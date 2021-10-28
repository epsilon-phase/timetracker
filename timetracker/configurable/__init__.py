"""
Provides an implementation of a configured property value, permitting storing changes, filters, etc

All values are stored in the top level of the json object, and then decoded using methods that may be associated with
them at runtime
"""
from __future__ import annotations

from typing import *
import json

from xdg import xdg_config_home
from functools import lru_cache

J = TypeVar('J', int, float, bool, dict['J', 'J'], list['J'])
X = TypeVar('X')


class ConfigTransform:
    """
    Holds functions for serializing and deserializing objects

    :ivar output: Converts an instance of an object to a json representation
    :ivar callable input: Converts an instance of json representation into the class.
    """
    __slots__ = ['input', 'output']
    input: Callable[[J], X]
    output: Callable[[X], J]

    def __init__(self, inp, output):
        self.input = inp
        self.output = output


def identity(obj: X) -> X:
    """
    Return the value passed to it

    :param obj: The value
    :return: The value
    """
    return obj


class ConfigStore:
    """
    a dictionary backed by a json configuration file.

    :ivar data: The json structure possessed
    :ivar transformers:
    """

    data: dict
    transformers: dict[str, ConfigTransform]

    def __init__(self, name: Optional[str]):
        """
        Initialize a new ConfigStore

        :param name: The name of the configuration store. Stored in an xdg-config directory, or None, which will result
        in no storage.
        """

        self.transformers = {}
        self.data = {}
        self.file = None
        if not name:
            return
        (xdg_config_home() / name).mkdir(parents=True, exist_ok=True)
        self.file = xdg_config_home() / name / "config.json"
        if not self.file.exists():
            self.file.touch(exist_ok=True)
            with self.file.open("w") as f:
                f.write("{}")
        with open(self.file, 'r') as f:
            try:
                self.data = json.load(f)
            except json.JSONDecodeError:
                print("Failed :/")
                self.data = {}

    @lru_cache(10)
    def get(self, key, default):
        """
        Get the (optionally computed) value from the configuration.

        Computations are set up with `add_transform`_

        :param key: The name of the value you want to get
        :param default: The value to return if the value is not present
        :return: The value associated with the key, or the default
        """
        if key in self.transformers.keys() and key in self.data.keys():
            return self.transformers[key].input(self.data[key])
        elif key in self.data.keys():
            return self.data[key]
        else:
            return default

    def set(self, key: str, value):
        """
        Set the value in the ConfigStore

        :param key: The name of the value in the ConfigStore
        :param value: the value to write to it.
        :return: None
        """
        ConfigStore.get.cache_clear()
        if key in self.transformers.keys():
            self.data[key] = self.transformers[key].output(value)
        else:
            self.data[key] = value
        if self.file is None:
            return
        with open(self.file, 'w') as f:
            try:
                s = json.dumps(self.data, indent=True)
                f.write(s)
            except IOError:
                print(f"Unable to write to {self.file}")

    def add_transform(self, name: str, input: Callable[[dict], X] = identity,
                      output: Callable[[X], dict] = identity) -> None:
        """
        Add a transform to convert a json object into another sort, based on the config key's name

        :param name: The name of the configuration key to attach this conversion to
        :param input: The function that converts the json into an instance of the desired object
        :param output: The function that converts the object into a json representation
        :return: None
        """
        ConfigStore.get.cache_clear()
        self.transformers[name] = ConfigTransform(input, output)

    def delete(self):
        """
        Remove the configuration file, also preventing this from being saved.
        """
        import os
        os.remove(self.file)
        os.rmdir(self.file.parent)
        self.file = None

    def __getitem__(self, item):
        return self.get(item, None)
