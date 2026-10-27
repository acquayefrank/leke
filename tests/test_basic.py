import leke


def test_leke_version():
    assert leke.version() == "0.1.0"
    assert leke.__version__ == "0.1.0"
