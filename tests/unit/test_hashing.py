from inova_av.domain.hashing import canonical_json_bytes, sha256_bytes


def test_canonical_json_is_independent_of_key_order() -> None:
    first = {"texto": "Diamantina", "version": 1}
    second = {"version": 1, "texto": "Diamantina"}
    assert canonical_json_bytes(first) == canonical_json_bytes(second)
    assert sha256_bytes(canonical_json_bytes(first)) == sha256_bytes(canonical_json_bytes(second))
