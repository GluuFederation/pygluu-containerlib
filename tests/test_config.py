import pytest

# ===========
# base config
# ===========


def test_config_get(gconfig):
    with pytest.raises(NotImplementedError) as exc:
        gconfig.get("foo")
    assert "" in str(exc.value)


def test_config_set(gconfig):
    with pytest.raises(NotImplementedError) as exc:
        gconfig.set("foo", "bar")
    assert "" in str(exc.value)


def test_config_all(gconfig):
    with pytest.raises(NotImplementedError) as exc:
        gconfig.all()
    assert "" in str(exc.value)

# =============
# consul config
# =============


def test_consul_config_token_from_file(gconsul_config, tmpdir):
    file_ = tmpdir.join("token_file")
    file_.write("random-token")
    assert gconsul_config._token_from_file(str(file_)) == "random-token"


def test_consul_config_verify_cert(gconsul_config, tmpdir):
    cacert_file = tmpdir.join("cacert.pem")
    cacert_file.write("cacert")

    cert_file = tmpdir.join("cert.pem")
    cert_file.write("cert")

    key_file = tmpdir.join("key.pem")
    key_file.write("key")

    cert, verify = gconsul_config._verify_cert(
        "https", True, str(cacert_file), str(cert_file), str(key_file),
    )
    assert cert == (str(cert_file), str(key_file))
    assert verify == str(cacert_file)


def test_consul_config_merge_path(gconsul_config):
    assert gconsul_config._merge_path("foo") == "gluu/config/foo"


def test_consul_config_unmerge_path(gconsul_config):
    assert gconsul_config._unmerge_path("gluu/config/foo") == "foo"


def test_consul_config_get(gconsul_config, monkeypatch):
    monkeypatch.setattr(
        "consul.Consul.KV.get",
        lambda cls, k: (1, {"Value": "bar"}),
    )
    assert gconsul_config.get("foo") == "bar"


def test_consul_config_get_default(gconsul_config, monkeypatch):
    monkeypatch.setattr(
        "consul.Consul.KV.get",
        lambda cls, k: (1, None),
    )
    assert gconsul_config.get("foo", "default") == "default"


def test_consul_config_set(gconsul_config, monkeypatch):
    monkeypatch.setattr(
        "consul.Consul.KV.put",
        lambda cls, k, v: True,
    )
    assert gconsul_config.set("foo", "bar") is True


def test_consul_config_all(gconsul_config, monkeypatch):
    monkeypatch.setattr(
        "consul.Consul.KV.get",
        lambda cls, k, recurse: (
            1,
            [
                {"Key": gconsul_config.prefix + "foo", "Value": "bar"},
                {"Key": gconsul_config.prefix + "lorem", "Value": "ipsum"},
            ],
        ),
    )
    assert gconsul_config.all() == {"foo": "bar", "lorem": "ipsum"}


def test_consul_config_all_empty(gconsul_config, monkeypatch):
    monkeypatch.setattr(
        "consul.Consul.KV.get",
        lambda cls, k, recurse: (
            1,
            [],
        ),
    )
    assert gconsul_config.all() == {}


def test_consul_config_request_warning(gconsul_config, caplog):
    gconsul_config._request_warning("https", False)
    assert "All requests to Consul will be unverified" in caplog.records[0].message
