from ask_my_docs_api.core.security import generate_api_key, hash_api_key


def test_abc_hash_is_valid():
    assert hash_api_key("abc") == "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad"


def test_same_key_has_same_hash():
    key = generate_api_key()
    assert hash_api_key(key) == hash_api_key(key)


def test_different_keys_have_different_hash():
    assert hash_api_key("key-a") != hash_api_key("key-b")


def test_generate_api_key_returns_diff_keys():
    assert generate_api_key() != generate_api_key()


def test_hash_len_is_valid():
    key = generate_api_key()
    assert len(hash_api_key(key)) == 64
