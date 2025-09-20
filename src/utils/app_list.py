# Placeholder for future script catalogs / JSON metadata parsing.
def list_scripts_from_folder(folder: str):
    import os
    return [os.path.join(folder, f) for f in os.listdir(folder) if f.lower().endswith(".ps1")]
