import os
from pathlib import Path
import pandas as pd
from imlib.general.config import get_config_obj
from amap.register.volume import calculate_volumes
from amap.config.atlas import Atlas
from imlib.source.source_files import source_custom_config_amap

volume_data_path = os.path.join("tests", "data", "register", "volume")
registered_atlas_path = os.path.join(volume_data_path, "registered_atlas.nii")
registered_hemispheres_path = os.path.join(
    volume_data_path, "registered_hemispheres.nii"
)
volumes_validate_path = os.path.join(volume_data_path, "volumes.csv")


def test_volume_calc(tmpdir):
    tmpdir = Path(tmpdir)
    atlas = Atlas(str(tmpdir.parent / "test_register0" / "config.conf"))
    structures_file_path = atlas.get_structures_path()
    print("struct file", structures_file_path)
    registration_config = source_custom_config_amap()

    volumes_csv_path = os.path.join(tmpdir, "volumes.csv")

    calculate_volumes(
        registered_atlas_path,
        registered_hemispheres_path,
        structures_file_path,
        registration_config,
        volumes_csv_path,
    )

    volumes_validate = pd.read_csv(
        volumes_validate_path, sep=",", header=0, quotechar='"'
    )
    volumes_test = pd.read_csv(
        volumes_csv_path, sep=",", header=0, quotechar='"'
    )
    print("volume tested")
    assert (volumes_validate == volumes_test).all().all()
