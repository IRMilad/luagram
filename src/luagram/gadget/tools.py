from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from lupa import _LuaTable



def arguments(func):
    def warp(cls, table: Optional['_LuaTable'] = None):
        args = []
        kwargs = {}
        
        if table is not None:
            for name, value in table.items():
                if isinstance(name, int):
                    args.append(value)
                
                else:
                    kwargs[name] = value 

        return func(cls, *args, **kwargs)

    return warp


