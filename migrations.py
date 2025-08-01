from alembic import op

def upgrade():
    op.create_table('users', users)
    op.create_table('posts', posts)
    op.create_table('files', files)

def downgrade():
    op.drop_table('users')
    op.drop_table('posts')
    op.drop_table('files')
