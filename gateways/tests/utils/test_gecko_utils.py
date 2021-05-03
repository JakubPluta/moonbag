from gateways.gecko.utils import find_discord


def test_should_properly_return_discord_if_exists():
    info = {"chat_url": ["https://discord.com/invite/NK4qdbv", "", ""]}
    assert (
        find_discord(info.get("chat_url"))
        == "https://discord.com/invite/NK4qdbv"
    )


def test_should_return_none_if_no_discord_or_no_object():
    info = {
        "chat_url": ["", "", ""],
    }
    info2 = {}

    assert find_discord(info.get("chat_url")) is None
    assert find_discord(info2.get("chat_url")) is None
