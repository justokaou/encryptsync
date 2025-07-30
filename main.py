import yaml

def load_config(path="config.yaml"):
    with open(path) as f:
        return yaml.safe_load(f)

if __name__ == "__main__":
    config = load_config()
    print("Configuration chargée :", config)