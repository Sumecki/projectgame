from app.auth.security import hash_password, verify_password

def test_hash_password_does_not_return_plain_password():
    password = "SecretPassword!"
    hashed_password = hash_password(password)

    assert password != hashed_password

def test_verify_password_returns_true_for_valid_password():
    password = "SecretPassword!"
    hashed_password = hash_password(password)

    assert verify_password(password, hashed_password) is True

def test_verify_password_returns_false_for_invalid_password():
    password = "SecretPassword!"
    wrong_password = "ThisIsInvalidPassword"
    hashed_password = hash_password(password)

    assert verify_password(wrong_password, hashed_password) is False
