from app.auth.security import hash_password, verify_password

class TestSecurityPassword:
    PASSWORD = "SecretPassword!"
    WRONG_PASSWORD = "InvalidPassword"

    def test_hash_password_returns_string(self):
        hashed_password = hash_password(self.PASSWORD)

        assert isinstance(hashed_password, str)

    def test_hash_password_does_not_return_plain_password(self):
        hashed_password = hash_password(self.PASSWORD)

        assert self.PASSWORD != hashed_password


    def test_verify_password_returns_true_for_valid_password(self):
        hashed_password = hash_password(self.PASSWORD)

        assert verify_password(self.PASSWORD, hashed_password) is True


    def test_verify_password_returns_false_for_invalid_password(self):
        hashed_password = hash_password(self.PASSWORD)

        assert verify_password(self.WRONG_PASSWORD, hashed_password) is False


    def test_hash_password_return_different_hashes_for_same_password(self):
        first_hash = hash_password(self.PASSWORD)
        second_hash = hash_password(self.PASSWORD)

        assert first_hash != second_hash
    