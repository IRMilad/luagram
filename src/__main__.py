import os
import lupa
import argparse
import importlib
from .luagram import LuagramClient, Params, Settings, BaseLogger, enums


LUA_VERSION = os.getenv('LUAGRAM_LUA_VERSION', 'jit')

__LUA_VERSIONS = {
    '5.1': 'lupa.lua51',
    '5.2': 'lupa.lua52',
    '5.3': 'lupa.lua53',
    '5.4': 'lupa.lua54',
    'jit': 'lupa.luajit21'
}


if not os.path.isdir('.app-data'):
    os.makedirs('.app-data')


def main():
    parser = argparse.ArgumentParser(description='Luagram')


    parser.add_argument('--name', '-n',
                        help='Session name', required=True)

    parser.add_argument('--script', '-s',
                        help='Path to the Lua script file',
                        type=argparse.FileType('r'), required=True)
    
    parser.add_argument('--version', '-v',
                        help='Lua Version', default=LUA_VERSION, choices=__LUA_VERSIONS.keys())

    
    arguments = parser.parse_args()
    with lupa.allow_lua_module_loading():
        LUA = importlib.import_module(__LUA_VERSIONS[arguments.version])

    lua_runtime = LUA.LuaRuntime(unpack_returned_tuples=True)
    variables = lua_runtime.globals()
    variables.name = arguments.name

    variables.enums = enums
    variables.Params = Params
    variables.Settings = Settings
    variables.BaseLogger = BaseLogger
    variables.create_new_client = LuagramClient

    return lua_runtime.execute(arguments.script.read())


if __name__ == '__main__':
    main()

