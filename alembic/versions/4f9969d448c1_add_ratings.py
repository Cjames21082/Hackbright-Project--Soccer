"""Add ratings

Revision ID: 4f9969d448c1
Revises: 43a4429e5537
Create Date: 2013-08-08 11:46:23.648907

"""

# revision identifiers, used by Alembic.
revision = '4f9969d448c1'
down_revision = '43a4429e5537'

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('games',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_date', sa.DateTime(), nullable=True),
    sa.Column('home_team', sa.Integer(), nullable=True),
    sa.Column('away_team', sa.Integer(), nullable=True),
    sa.Column('home_score', sa.Integer(), nullable=True),
    sa.Column('away_score', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['away_team'], ['teams.id'], ),
    sa.ForeignKeyConstraint(['home_team'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('player_ratings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('team_rating', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('player_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('goals', sa.Integer(), nullable=True),
    sa.Column('absence', sa.Boolean(), nullable=True),
    sa.Column('goalie_win', sa.Boolean(), nullable=True),
    sa.Column('goalie_loss', sa.Boolean(), nullable=True),
    sa.Column('assists', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('team_ratings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('team_rating', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.add_column(u'season_cycles', sa.Column('active', sa.Boolean(), nullable=True))
    op.add_column(u'users', sa.Column('strength', sa.Integer(), nullable=True))
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_column(u'users', 'strength')
    op.drop_column(u'season_cycles', 'active')
    op.drop_table('team_ratings')
    op.drop_table('player_stats')
    op.drop_table('player_ratings')
    op.drop_table('games')
    op.drop_table('posts')
    ### end Alembic commands ###
