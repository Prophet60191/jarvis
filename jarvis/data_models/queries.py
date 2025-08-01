from sqlalchemy import func

def get_user_posts(user_id):
    return session.query(Post).filter_by(user_id=user_id).all()

def get_file_info(file_id):
    return session.query(File).filter_by(id=file_id).first()
