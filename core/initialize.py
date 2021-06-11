from core import config as configurator, db

config = configurator.configure()
db = db.connect(config['mongodb'])