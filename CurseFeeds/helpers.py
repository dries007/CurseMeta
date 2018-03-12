from . import *


def get_all_supported_feeds(gamesfeeddata: [dict]=None):
    if gamesfeeddata is None:
        gamesfeeddata = GamesFeed().load_feed()['data']
    return [AddonsFeed(supported['ID']) for supported in filter(lambda x: x['SupportsAddons'], gamesfeeddata)]

