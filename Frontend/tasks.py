from celery import Celery

from . import celery
from . import curse
from . import db
from .models import AddonModel
from .models import FileModel


@celery.on_after_configure.connect
def setup_periodic_tasks(sender: Celery, **kwargs):
    sender.add_periodic_task(60*60, periodic_curse_login.s())
    sender.add_periodic_task(15*60, periodic_ill_missing_addons.s())


@celery.task
def periodic_curse_login():
    return curse.login_client.checklogin()


@celery.task
def periodic_ill_missing_addons():
    for x in AddonModel.query.filter(AddonModel.name is None).all():
        curse.service.GetAddOn(x.id)


@celery.task
def fill_missing_addon(addon_id: int):
    addon = AddonModel.query.get(addon_id)
    if addon is None or addon.name is None:
        curse.service.GetAddOn(addon_id)
        return True
    return False


@celery.task
def analyse_direct_result(name: str, inp: dict, outp: dict):
    # Deconstructs the return types of complex data returns into 'core' components for analysis
    if name == 'GetAddOn':
        AddonModel.update(outp)
    elif name == 'GetRepositoryMatchFromSlug':
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
            for f in o['LatestFiles']:
                FileModel.update(o['Id'], f)
    elif name == 'GetFuzzyMatches':
        for o in outp:
            FileModel.update(o['Id'], o['File'])
            for f in o['LatestFiles']:
                FileModel.update(o['Id'], f)
    elif name == 'GetAllFilesForAddOn':
        for o in outp:
            FileModel.update(inp['addOnID'], o)
    elif name == 'GetAddOnFiles':
        for o in outp:
            if o['Value']:
                FileModel.update(o['Key'], o['Value'])
    else:
        return False
    db.session.commit()
