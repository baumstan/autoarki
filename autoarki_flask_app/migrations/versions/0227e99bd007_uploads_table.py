"""uploads table

Revision ID: 0227e99bd007
Revises: 8a80adff3faa
Create Date: 2022-02-19 23:58:56.961791

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0227e99bd007'
down_revision = '8a80adff3faa'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('image_upload', sa.Column('image', sa.String(length=140), nullable=True))
    op.drop_column('image_upload', 'body')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('image_upload', sa.Column('body', sa.VARCHAR(length=140), nullable=True))
    op.drop_column('image_upload', 'image')
    # ### end Alembic commands ###