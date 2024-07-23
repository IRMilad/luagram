import os
import argparse
from .luagram import LuagramClient, Params, Settings, BaseLogger, enums


try:
    import lupa.luajit21 as lupa

except ImportError:
    try:
        import lupa.lua54 as lupa

    except ImportError:
        try:
            import lupa.lua53 as lupa

        except ImportError:
            import lupa


if not os.path.isdir('.app-data'):
    os.makedirs('.app-data')


lua = lupa.LuaRuntime(unpack_returned_tuples=True)
variables = lua.globals()
variables.enums = enums
variables.Params = Params
variables.Settings = Settings
variables.BaseLogger = BaseLogger
variables.create_new_client = LuagramClient


def main():
    parser = argparse.ArgumentParser(description='Luagram')


    parser.add_argument('--name', '-n',
                        help='Session name', required=True)

    parser.add_argument('--script', '-s',
                        help='Path to the Lua script file',
                        type=argparse.FileType('r'), required=True)

    variables = lua.globals()
    arguments = parser.parse_args()

    variables.name = arguments.name

    return lua.execute(arguments.script.read())


if __name__ == '__main__':
    main()

