from foundry_local_sdk import Configuration, FoundryLocalManager

from config import APP_NAME

_yonetici = None


def get_manager():
    global _yonetici
    if _yonetici is None:
        yapilandirma = Configuration(app_name=APP_NAME)
        FoundryLocalManager.initialize(yapilandirma)
        _yonetici = FoundryLocalManager.instance
    return _yonetici


def load_model(model_alias, show_progress=False):
    yonetici = get_manager()
    model = yonetici.catalog.get_model(model_alias)
    if show_progress:
        model.download(lambda yuzde: print(f"\r{model_alias} indiriliyor: %{yuzde:.1f}", end=""))
        print()
    else:
        model.download()
    model.load()
    return model
