from core import config as configurator, db

config = configurator.configure()
dbclient = db.connect(config['mongodb'])
db = db.init(dbclient)
mode = 'initial'
