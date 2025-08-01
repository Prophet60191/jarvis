from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import Base

engine = create_engine('postgresql://user:password@localhost/dbname')
Session = sessionmaker(bind=engine)

def get_session():
    return Session()

def add_user(username, email, password):
    user = User(username=username, email=email, password=password)
    session = get_session()
    session.add(user)
    session.commit()

def add_post(user_id, content):
    post = Post(user_id=user_id, content=content)
    session = get_session()
    session.add(post)
    session.commit()

def add_file(user_id, filename, filepath):
    file = File(user_id=user_id, filename=filename, filepath=filepath)
    session = get_session()
    session.add(file)
    session.commit()
