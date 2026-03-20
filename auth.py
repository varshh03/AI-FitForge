import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import os
import bcrypt

CONFIG_FILE = "config.yaml"

def initialize_config():
    if not os.path.exists(CONFIG_FILE):
        config = {
            "credentials": {
                "usernames": {}
            },
            "cookie": {
                "expiry_days": 30,
                "key": "fitforge_secret_key",
                "name": "fitforge_cookie"
            }
        }
        with open(CONFIG_FILE, "w") as f:
            yaml.dump(config, f)

def load_config():
    initialize_config()
    with open(CONFIG_FILE) as f:
        return yaml.load(f, Loader=SafeLoader)

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        yaml.dump(config, f)

def register_user(username, name, password):
    config = load_config()

    if username in config["credentials"]["usernames"]:
        return False, "Username already exists!"

    hashed_password = bcrypt.hashpw(
        password.encode("utf-8"),
        bcrypt.gensalt()
    ).decode("utf-8")

    config["credentials"]["usernames"][username] = {
        "name": name,
        "password": hashed_password
    }

    save_config(config)
    return True, "Registration successful!"

def get_authenticator():
    config = load_config()
    authenticator = stauth.Authenticate(
        config["credentials"],
        config["cookie"]["name"],
        config["cookie"]["key"],
        config["cookie"]["expiry_days"]
    )
    return authenticator, config