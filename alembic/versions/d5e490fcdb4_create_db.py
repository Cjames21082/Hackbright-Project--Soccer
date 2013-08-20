"""create db

Revision ID: d5e490fcdb4
Revises: None
Create Date: 2013-08-19 11:16:58.326774

"""

# revision identifiers, used by Alembic.
revision = 'd5e490fcdb4'
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.create_table('health_types',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('issue', sa.String(length=64), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('firstname', sa.String(length=64), nullable=True),
    sa.Column('lastname', sa.String(length=64), nullable=True),
    sa.Column('email', sa.String(length=120), nullable=True),
    sa.Column('password', sa.String(length=64), nullable=True),
    sa.Column('address', sa.String(length=120), nullable=True),
    sa.Column('city', sa.String(length=64), nullable=True),
    sa.Column('state', sa.String(length=64), nullable=True),
    sa.Column('zipcode', sa.String(length=64), nullable=True),
    sa.Column('country', sa.String(length=64), nullable=True),
    sa.Column('role', sa.Integer(), nullable=True),
    sa.Column('gender', sa.String(length=64), nullable=True),
    sa.Column('fitness', sa.Integer(), nullable=True),
    sa.Column('experience', sa.Integer(), nullable=True),
    sa.Column('dob', sa.Date(), nullable=True),
    sa.Column('willing_teamLeader', sa.Boolean(), nullable=True),
    sa.Column('about_me', sa.String(length=140), nullable=True),
    sa.Column('last_seen', sa.DateTime(), nullable=True),
    sa.Column('user_disabled', sa.Boolean(), nullable=True),
    sa.Column('user_registered', sa.Boolean(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('season_cycles',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('admin_id', sa.Integer(), nullable=True),
    sa.Column('leaguename', sa.String(length=64), nullable=True),
    sa.Column('cyclename', sa.String(length=64), nullable=True),
    sa.Column('num_of_teams', sa.Integer(), nullable=True),
    sa.Column('home_region', sa.String(length=64), nullable=True),
    sa.Column('fee_resident', sa.Float(), nullable=True),
    sa.Column('fee_nonresident', sa.Float(), nullable=True),
    sa.Column('reg_start', sa.DateTime(), nullable=True),
    sa.Column('reg_end', sa.DateTime(), nullable=True),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('saved', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('users_health',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('health_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['health_id'], ['health_types.id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('positions',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('position_type', sa.String(length=64), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('posts',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('body', sa.String(length=140), nullable=True),
    sa.Column('timestamp', sa.DateTime(), nullable=True),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('teams',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('seasoncycle', sa.Integer(), nullable=True),
    sa.Column('teamname', sa.String(length=64), nullable=True),
    sa.Column('team_wins', sa.Integer(), nullable=True),
    sa.Column('team_ties', sa.Integer(), nullable=True),
    sa.Column('team_losses', sa.Integer(), nullable=True),
    sa.Column('team_goals', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['seasoncycle'], ['season_cycles.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('games',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_date', sa.Date(), nullable=True),
    sa.Column('home_team', sa.Integer(), nullable=True),
    sa.Column('away_team', sa.Integer(), nullable=True),
    sa.Column('home_score', sa.Integer(), nullable=True),
    sa.Column('away_score', sa.Integer(), nullable=True),
    sa.Column('game_saved', sa.Boolean(), nullable=True),
    sa.Column('home_win', sa.Integer(), nullable=True),
    sa.Column('away_win', sa.Integer(), nullable=True),
    sa.Column('home_tie', sa.Float(), nullable=True),
    sa.Column('away_tie', sa.Float(), nullable=True),
    sa.Column('home_loss', sa.Integer(), nullable=True),
    sa.Column('away_loss', sa.Integer(), nullable=True),
    sa.Column('home_differential', sa.Float(), nullable=True),
    sa.Column('away_differential', sa.Float(), nullable=True),
    sa.Column('expectation', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['away_team'], ['teams.id'], ),
    sa.ForeignKeyConstraint(['home_team'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('team_members',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('team_leader', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['player_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
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
    op.create_table('player_stats',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('goals', sa.Integer(), nullable=True),
    sa.Column('absence', sa.Boolean(), nullable=True),
    sa.Column('goalie_win', sa.Boolean(), nullable=True),
    sa.Column('goalie_loss', sa.Boolean(), nullable=True),
    sa.Column('assists', sa.Integer(), nullable=True),
    sa.Column('strength', sa.Integer(), nullable=True),
    sa.Column('stat_saved', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('player_ratings',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('team_id', sa.Integer(), nullable=True),
    sa.Column('game_id', sa.Integer(), nullable=True),
    sa.Column('player_id', sa.Integer(), nullable=True),
    sa.Column('player_rating', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['game_id'], ['games.id'], ),
    sa.ForeignKeyConstraint(['player_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['team_id'], ['teams.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    ### end Alembic commands ###


def downgrade():
    ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('player_ratings')
    op.drop_table('player_stats')
    op.drop_table('team_ratings')
    op.drop_table('team_members')
    op.drop_table('games')
    op.drop_table('teams')
    op.drop_table('posts')
    op.drop_table('positions')
    op.drop_table('users_health')
    op.drop_table('season_cycles')
    op.drop_table('users')
    op.drop_table('health_types')
    ### end Alembic commands ###
