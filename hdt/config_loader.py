import yaml

def load_units_config(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)

def load_sim_params(path):
    with open(path, "r") as f:
        return yaml.safe_load(f)
