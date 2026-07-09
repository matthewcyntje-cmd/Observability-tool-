def get_brand_name(config_path):
    with open(config_path) as f:
        lines = [line.strip() for line in f if line.strip()]
    return lines[-1] if lines else None


def get_api_key(key_path):
    with open(key_path) as f:
        lines = [line.strip() for line in f if line.strip()]
    if not lines:
        raise ValueError(
            f"No API key found in {key_path}. Paste your Anthropic API key into that file."
        )
    return lines[-1]
