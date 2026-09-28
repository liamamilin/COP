from app.core.security import SecretCipher, secret_hint


def test_secret_cipher_round_trip_and_masking() -> None:
    cipher = SecretCipher("test-secret")
    encrypted = cipher.encrypt("sk-example-123456")
    assert "sk-example" not in encrypted
    assert cipher.decrypt(encrypted) == "sk-example-123456"
    assert secret_hint("sk-example-123456") == "••••3456"
