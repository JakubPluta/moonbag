def find_discord(item: list) -> list or None:
    if isinstance(item, list) and len(item) > 0:
        discord = [chat for chat in item if "discord" in chat]
        if len(discord) > 0:
            return discord[0]


def filter_list(lst: list) -> list:
    if isinstance(lst, list) and len(lst) > 0:
        return [i for i in lst if i != ""]
