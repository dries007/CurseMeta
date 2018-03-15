from .taskhelpers import *

from ..models import AddonModel
from ..models import FileModel


@celery.task
def analyse_direct_result(name: str, inp: dict, outp: dict):
    # Deconstructs the return types of complex data returns into 'core' components for analysis
    # noinspection PyBroadException
    try:
        if name == 'GetAddOn':
            AddonModel.update(outp)
        elif name == 'GetRepositoryMatchFromSlug':
            if outp['LatestFiles'] is not None:
                for f in outp['LatestFiles']:
                    FileModel.update(outp['Id'], f)
        elif name == 'GetAddOnFile':
            FileModel.update(inp['addonID'], outp)
        elif name == 'v2GetAddOns':
            for f in outp:
                AddonModel.update(f)
        elif name == 'v2GetFingerprintMatches':
            for x in ('ExactMatches', 'PartialMatches'):
                o = outp[x]
                FileModel.update(o['Id'], o['File'])
                if o['LatestFiles'] is not None:
                    for f in o['LatestFiles']:
                        FileModel.update(o['Id'], f)
        elif name == 'GetFuzzyMatches':
            for o in outp:
                FileModel.update(o['Id'], o['File'])
                if o['LatestFiles'] is not None:
                    for f in o['LatestFiles']:
                        FileModel.update(o['Id'], f)
        elif name == 'GetAllFilesForAddOn':
            for o in outp:
                FileModel.update(inp['addOnID'], o)
        elif name == 'GetAddOnFiles':
            for o in outp:
                if o['Value']:
                    for f in o['Value']:
                        FileModel.update(o['Key'], f)
        else:
            return False
        db.session.commit()
    except Exception:
        logger.exception('Error analyse_direct_result with {}: {} -> {}'.format(name, inp, outp))

