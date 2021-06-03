def get_slug_mappings(lst: list):
    mappings = {}
    for item in lst:
        if item.get("slug") is not None:
            mappings[item["slug"].lower()] = item.get("name").lower()
        else:
            mappings[item["name"].lower()] = item.get("name").lower()
    return mappings
