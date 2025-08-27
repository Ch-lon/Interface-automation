# -*- coding: utf-8 -*-
import codecs
import inspect
import json
import os
import re
from enum import Enum, unique
from functools import wraps

try:
    import yaml
except ImportError:
    _have_yaml = False
else:
    _have_yaml = True

__version__ = '1.4.1'

DATA_ATTR = '%values'
FILE_ATTR = '%file_path'
YAML_LOADER_ATTR = '%yaml_loader'
UNPACK_ATTR = '%unpack'
index_len = 5


try:
    trivial_types = (type(None), bool, int, float, basestring)
except NameError:
    trivial_types = (type(None), bool, int, float, str)


@unique
class TestNameFormat(Enum):
    DEFAULT = 0
    INDEX_ONLY = 1


def is_trivial(value):
    if isinstance(value, trivial_types):
        return True
    elif isinstance(value, (list, tuple)):
        return all(map(is_trivial, value))
    return False


def unpack(func):
    setattr(func, UNPACK_ATTR, True)
    return func


def data(*values):
    global index_len
    index_len = len(str(len(values)))
    return idata(values)


def idata(iterable):
    def wrapper(func):
        setattr(func, DATA_ATTR, iterable)
        return func
    return wrapper


def file_data(value, yaml_loader=None):
    def wrapper(func):
        setattr(func, FILE_ATTR, value)
        if yaml_loader:
            setattr(func, YAML_LOADER_ATTR, yaml_loader)
        return func
    return wrapper


def mk_test_name(name, value, index=0, name_fmt=TestNameFormat.DEFAULT):
    index = "{0:0{1}}".format(index + 1, index_len)
    if name_fmt is TestNameFormat.INDEX_ONLY:
        return "{0}_{1}".format(name, index)
    if not is_trivial(value):
        return "{0}_{1}".format(name, index)
    try:
        value_str = str(value).replace(" ", "_").replace("；", "_").replace(";", "_")
        value_str = re.sub(r'\W+', '_', value_str)
    except:
        value_str = "unknown"
    return "{0}_{1}_{2}".format(name, index, value_str)


def feed_data(func, new_name, test_data_docstring, *args, **kwargs):
    @wraps(func)
    def wrapper(self):
        return func(self, *args, **kwargs)
    wrapper.__name__ = new_name
    wrapper.__wrapped__ = func
    if test_data_docstring is not None:
        wrapper.__doc__ = test_data_docstring
    else:
        if func.__doc__:
            try:
                wrapper.__doc__ = func.__doc__.format(*args, **kwargs)
            except (IndexError, KeyError):
                pass
    return wrapper


def add_test(cls, test_name, test_docstring, func, *args, **kwargs):
    setattr(cls, test_name, feed_data(func, test_name, test_docstring, *args, **kwargs))


def process_file_data(cls, name, func, file_attr):
    cls_path = os.path.abspath(inspect.getsourcefile(cls))
    data_file_path = os.path.join(os.path.dirname(cls_path), file_attr)

    def create_error_func(message):
        def func(*args):
            raise ValueError(message % file_attr)
        return func

    if not os.path.exists(data_file_path):
        test_name = mk_test_name(name, "error")
        test_docstring = """Error!"""
        add_test(cls, test_name, test_docstring, create_error_func("%s does not exist"), None)
        return

    _is_yaml_file = data_file_path.endswith((".yml", ".yaml"))

    if _is_yaml_file and not _have_yaml:
        test_name = mk_test_name(name, "error")
        test_docstring = """Error!"""
        add_test(
            cls,
            test_name,
            test_docstring,
            create_error_func("%s is a YAML file, please install PyYAML"),
            None
        )
        return

    with codecs.open(data_file_path, 'r', 'utf-8') as f:
        if _is_yaml_file:
            if hasattr(func, YAML_LOADER_ATTR):
                yaml_loader = getattr(func, YAML_LOADER_ATTR)
                data = yaml.load(f, Loader=yaml_loader)
            else:
                data = yaml.safe_load(f)
        else:
            data = json.load(f)

    _add_tests_from_data(cls, name, func, data)


def _add_tests_from_data(cls, name, func, data):
    for i, elem in enumerate(data):
        if isinstance(data, dict):
            key, value = elem, data[elem]
            test_name = mk_test_name(name, key, i)
        elif isinstance(data, list):
            value = elem
            test_name = mk_test_name(name, value, i)
        if isinstance(value, dict):
            add_test(cls, test_name, test_name, func, **value)
        else:
            add_test(cls, test_name, test_name, func, value)


def _is_primitive(obj):
    return not hasattr(obj, '__dict__')


def _get_test_data_docstring(func, value):
    return value.get('title')
    if not _is_primitive(value) and value.__doc__:
        return value.__doc__
    else:
        return None


def ddt(arg=None, **kwargs):
    fmt_test_name = kwargs.get("testNameFormat", TestNameFormat.DEFAULT)

    def wrapper(cls):
        for name, func in list(cls.__dict__.items()):
            if hasattr(func, DATA_ATTR):
                for i, v in enumerate(getattr(func, DATA_ATTR)):
                    test_name = mk_test_name(
                        name,
                        getattr(v, "__name__", v),
                        i,
                        fmt_test_name
                    )
                    test_data_docstring = _get_test_data_docstring(func, v)
                    if hasattr(func, UNPACK_ATTR):
                        if isinstance(v, tuple) or isinstance(v, list):
                            add_test(
                                cls,
                                test_name,
                                test_data_docstring,
                                func,
                                *v
                            )
                        else:
                            add_test(
                                cls,
                                test_name,
                                test_data_docstring,
                                func,
                                **v
                            )
                    else:
                        add_test(cls, test_name, test_data_docstring, func, v)
                # ✅ 不再删除原始方法
                # delattr(cls, name)  # 注释掉这行，保留原始方法
            elif hasattr(func, FILE_ATTR):
                file_attr = getattr(func, FILE_ATTR)
                process_file_data(cls, name, func, file_attr)
                # ✅ 不再删除原始方法
                # delattr(cls, name)  # 注释掉这行，保留原始方法
        return cls

    return wrapper(arg) if inspect.isclass(arg) else wrapper