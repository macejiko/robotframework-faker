import ast

import faker
import faker.generator
from robot.api import logger

"""

This is a very thin wrapper for faker. You can access all of faker's usual methods
via FakerLibrary calls in Robot Framework.

"""


class FakerKeywords(object):
    """ 
    This looks tricky but it's just the Robot Framework Hybrid Library API. 
    http://robotframework.googlecode.com/hg/doc/userguide/RobotFrameworkUserGuide.html#hybrid-library-api
    """
    
    ROBOT_LIBRARY_SCOPE = 'Global'
    _fake = faker.Faker()

    def __init__(self, locale=None, providers=None, seed=None):
        self._fake = faker.Faker(locale, providers)
        if seed:
            self._fake.seed(seed)

    def get_keyword_names(self):
        keywords = [name for name, function in self._fake.__dict__.items() if
                    hasattr(function, '__call__')]

        keywords.extend([name for name, function in
                         faker.generator.Generator.__dict__.items() if
                         hasattr(function, '__call__')])
        return keywords

    def __getattr__(self, name):
        func = None
        if name in self._fake.__dict__.keys():
            func = getattr(self._fake, name)
        elif name in faker.generator.Generator.__dict__.keys():
            func = faker.generator.Generator.__dict__[name]
        if func:
            # when running libdoc, need to disable this decorator temporarily
            # to allow for RF's introspection
            return _str_vars_to_data(func)
        raise AttributeError('Non-existing keyword "{0}"'.format(name))


def _str_to_data(string):
    try:
        return ast.literal_eval(str(string).strip())
    except Exception:
        return string


def _str_vars_to_data(f):
    def wrapped(*args, **kwargs):
        args = [_str_to_data(arg) for arg in args]
        kwargs = dict((arg_name, _str_to_data(arg)) for arg_name, arg in kwargs.items())
        result = f(*args, **kwargs)
        logger.debug(result)
        return result
    return wrapped
