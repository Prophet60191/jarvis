def validate_user_data(username, email, password):
    if not username or not email or not password:
        raise ValueError('Invalid user data')
    return True

def validate_post_data(content):
    if not content:
        raise ValueError('Invalid post data')
    return True

def validate_file_data(filename, filepath):
    if not filename or not filepath:
        raise ValueError('Invalid file data')
    return True
