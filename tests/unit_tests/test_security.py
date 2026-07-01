import pytest

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

    def test_hash_password_returns_different_hashes_for_same_password(self):
        first_hash = hash_password(self.PASSWORD)
        second_hash = hash_password(self.PASSWORD)

        assert first_hash != second_hash

    @pytest.mark.parametrize(
        ("password", "expected_result"),
        [
            pytest.param(PASSWORD, True, id="valid-password"),
            pytest.param(WRONG_PASSWORD, False, id="invalid-password"),
        ],
    )
    def test_verify_password_returns_expected_result(
        self,
        password: str,
        expected_result: bool,
    ):
        hashed_password = hash_password(self.PASSWORD)

        assert verify_password(password, hashed_password) is expected_result
