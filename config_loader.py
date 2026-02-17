import random

CONFIG_FILE = "configs.txt"

def get_random_config():
    try:
        with open(CONFIG_FILE, "r", encoding="utf-8") as f:
            configs = [line.strip() for line in f if line.strip()]
        if not configs:
            return None
        return random.choice(configs)
    except:
        return None
