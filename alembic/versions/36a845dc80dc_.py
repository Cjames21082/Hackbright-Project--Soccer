"""empty message

Revision ID: 36a845dc80dc
Revises: 21c7af9aa63c
Create Date: 2013-08-14 17:04:51.231071

"""

# revision identifiers, used by Alembic.
revision = '36a845dc80dc'
down_revision = '21c7af9aa63c'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('games', u'game_date')
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.add_column('games', sa.Column(u'game_date', postgresql.TIMESTAMP(), nullable=True))
    ### end Alembic commands ###
