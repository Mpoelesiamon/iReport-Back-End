"""add migration

Revision ID: d8dd88d197f8
Revises: 
Create Date: 2024-03-19 23:20:41.626348

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd8dd88d197f8'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(), nullable=False),
    sa.Column('email', sa.String(), nullable=False),
    sa.Column('_password_hash', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('role', sa.String(), nullable=False),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('interventionrecord',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('users_id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('images', sa.String(), nullable=False),
    sa.Column('videos', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['users_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('redflagrecord',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('users_id', sa.Integer(), nullable=False),
    sa.Column('description', sa.String(), nullable=False),
    sa.Column('images', sa.String(), nullable=False),
    sa.Column('videos', sa.String(), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['users_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('adminaction',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('redflagrecords_id', sa.Integer(), nullable=False),
    sa.Column('interventionrecords_id', sa.Integer(), nullable=False),
    sa.Column('action_type', sa.String(), nullable=True),
    sa.Column('comments', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), nullable=True),
    sa.Column('updated_at', sa.DateTime(), nullable=True),
    sa.ForeignKeyConstraint(['interventionrecords_id'], ['interventionrecord.id'], ),
    sa.ForeignKeyConstraint(['redflagrecords_id'], ['redflagrecord.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('adminaction')
    op.drop_table('redflagrecord')
    op.drop_table('interventionrecord')
    op.drop_table('user')
    # ### end Alembic commands ###
