"""Initialize User entity

Revision ID: 5ef69ec74a32
Revises: 
Create Date: 2022-01-13 15:10:16.237503

"""
from alembic import op
import sqlalchemy as sa
from app.database.schema import GUID

# revision identifiers, used by Alembic.
revision = '5ef69ec74a32'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False, comment='PK user id'),
    sa.Column('uuid', GUID(), nullable=True, comment='uuid'),
    sa.Column('status', sa.Enum('active', 'deleted', 'blocked'), nullable=True, comment='계정 상태'),
    sa.Column('email', sa.String(length=255), nullable=False, comment='이메일'),
    sa.Column('pw', sa.String(length=2000), nullable=False, comment='비밀번호'),
    sa.Column('nickname', sa.String(length=255), nullable=False, comment='닉네임'),
    sa.Column('phone_number', sa.String(length=20), nullable=True, comment='전화번호'),
    sa.Column('profile_img', sa.String(length=1000), nullable=True, comment='프로필 이미지'),
    sa.Column('created_at', sa.DateTime(), nullable=False, comment='생성일자'),
    sa.Column('updated_at', sa.DateTime(), nullable=False, comment='최종 수정 일자'),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('phone_number')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###