try:
    from Frontend import manager
except ImportError:
    from . import manager

manager.run()
