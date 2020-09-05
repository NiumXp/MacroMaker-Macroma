from re import compile, finditer, match
from string import whitespace
from collections import defaultdict
from enum import Enum

from .environment import Environment
from . import errors

def unify_environments(envs):
    main, *envs = envs
    for env in envs:
        main.functions.update(env.function)
        main.attributes.update(env.attributes)

    return main


class EnvironmentType(Enum):
    pass


def parse(string) -> tuple:
    args = []

    temp = ''
    ignore = False
    for character in string:
        if character == '"':
            ignore = not ignore

        if character == ',':
            if not ignore:
                args.append(temp.strip(" '\""))
                temp = ''
                continue

        temp += character

    args.append(temp.strip(" '\""))

    return args


class MacroMa:
    ACTION_REGEX = compile(r"(:?[\w\-]*)\s*\(((?:[^()])*)\)")
    LINE_REGEX = compile(r"(?:[^()])*?;")
    PARSER_REGEX = compile(r"(.+?) +(.*)")

    def __init__(self):
        self.__scripts = {}
        self.__environments = {}

    def load_script(self, data: str, name: str):
        if not isinstance(data, str):
            raise TypeError("str expected in `data` parameter")

        environments = []
        guide = defaultdict(lambda: list())
        for group in finditer(self.ACTION_REGEX, data):
            name_, content = group.groups()

            for line in finditer(self.LINE_REGEX, content):
                line = line.group().strip(whitespace + ';')

                if name_.startswith(':'):
                    environments.append(line)
                else:
                    action, presets = match(r"(.+?) +(.*)", line).groups()

                    guide[name_].append([action, parse(presets)])

        self.__scripts[name] = [environments, dict(guide)]

    def load_environment(self, env):
        if not issubclass(env, Environment):
            raise TypeError("macroma.Enviroment expected in `env` parameter")

        self.__environments[env.__name__] = env

    def run_script(self, name: str):
        environments, groups = self.__scripts[name]

        for index, environment in enumerate(environments):
            try:
                environment = self.__environments[environment]
            except KeyError:
                raise errors.EnvironmentNotFoundError(environment)
            else:
                environments[index] = environment(self)

        environment = unify_environments(environments)

        for group, actions in groups.items():
            for index, action in enumerate(actions):
                function, args = action

                try:
                    function = environment.functions[function]
                except KeyError:
                    raise errors.FunctionNotFoundError(function)
                else:
                    function.env = environment

                for index_, arg in enumerate(args):
                    try:
                        arg = environment.attributes[arg]
                    except KeyError:
                        pass

                    args[index_] = arg

                actions[index] = (function, args)
            groups[group] = actions

        for name, actions in groups.items():
            for action in actions:
                function, args = action
                function(*args)
