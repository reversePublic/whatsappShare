import os

APP_DATA = {
    "gc.whatsappprotocolregisterapi": 1,
    "gc.whatsappprotocolexportgroup": 2,
    "gc.playapi": 3,
    "gc.groupmessagecatchapi": 4
}


def app_env():
    app = os.getenv('APP')
    app_type = APP_DATA.get(app)
    return app_type
