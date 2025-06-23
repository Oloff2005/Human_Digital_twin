import shutil
import os

PROFILE_MAP = {
    "1": "units_config_beginner.yaml",
    "2": "units_config_active.yaml",
    "3": "units_config_athlete.yaml"
}

def backup_existing_config():
    config_path = "hdt/config/units_config.yaml"
    if os.path.exists(config_path):
        i = 1
        while os.path.exists(f"hdt/config/units_config_backup_v{i}.yaml"):
            i += 1
        backup_path = f"hdt/config/units_config_backup_v{i}.yaml"
        shutil.copyfile(config_path, backup_path)
        print(f"📦 Existing config backed up as: {backup_path}")

def select_profile():
    print("🎯 Select your profile:\n")
    print("[1] Beginner  – Low fitness, not actively training")
    print("[2] Active    – Moderate fitness, regular exercise")
    print("[3] Athlete   – High-performance or competitive athlete\n")

    choice = input("Enter choice [1–3]: ").strip()
    if choice not in PROFILE_MAP:
        print("❌ Invalid choice. Please run again and select 1, 2, or 3.")
        return

    src = f"hdt/config/{PROFILE_MAP[choice]}"
    dst = "hdt/config/units_config.yaml"

    if not os.path.exists(src):
        print(f"❌ Profile config file not found: {src}")
        return

    backup_existing_config()
    shutil.copyfile(src, dst)
    print(f"\n✅ {PROFILE_MAP[choice]} loaded as your active configuration.")

if __name__ == "__main__":
    select_profile()
