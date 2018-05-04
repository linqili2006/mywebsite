#!flask/bin/python
from migrate.versioning import api
from config import SQLALCHEMY_DATABASE_URI
from config import SQLALCHEMY_MIGRATE_REPO
from app import db, models
import os.path
db.create_all()
admin = models.Judge(name='admin', passwd='21232f297a57a5a743894a0e4a801fc3')
db.session.add(admin)
db.session.commit()
if not os.path.exists(SQLALCHEMY_MIGRATE_REPO):
    api.create(SQLALCHEMY_MIGRATE_REPO, 'database repository')
    api.version_control(SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_MIGRATE_REPO)
else:
    api.version_control(SQLALCHEMY_DATABASE_URI,
    SQLALCHEMY_MIGRATE_REPO,
    api.version(SQLALCHEMY_MIGRATE_REPO))
