from sqlalchemy import *
from migrate import *


from migrate.changeset import schema
pre_meta = MetaData()
post_meta = MetaData()
health_type = Table('health_type', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('issue', String(length=64)),
)

position = Table('position', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('positionType', String(length=64)),
)

user_health = Table('user_health', post_meta,
    Column('id', Integer, primary_key=True, nullable=False),
    Column('user_id', Integer),
    Column('health_id', Integer),
)


def upgrade(migrate_engine):
    # Upgrade operations go here. Don't create your own engine; bind
    # migrate_engine to your metadata
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['health_type'].create()
    post_meta.tables['position'].create()
    post_meta.tables['user_health'].create()


def downgrade(migrate_engine):
    # Operations to reverse the above upgrade go here.
    pre_meta.bind = migrate_engine
    post_meta.bind = migrate_engine
    post_meta.tables['health_type'].drop()
    post_meta.tables['position'].drop()
    post_meta.tables['user_health'].drop()
