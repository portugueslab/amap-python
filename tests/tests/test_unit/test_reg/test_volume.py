import os

import pandas as pd

from amap.register.volume import calculate_volumes
from amap.config.atlas import Atlas
from imlib.source.source_files import source_custom_config_amap
from imlib.general.config import get_config_obj

volume_data_path = os.path.join("tests", "data", "register", "volume")
registered_atlas_path = os.path.join(volume_data_path, "registered_atlas.nii")
registered_hemispheres_path = os.path.join(
    volume_data_path, "registered_hemispheres.nii"
)
volumes_validate_path = os.path.join(volume_data_path, "volumes.csv")


def test_volume_calc(tmpdir, test_config_path):
    tmpdir = str(tmpdir)
    atlas = Atlas(test_config_path)

    structures_file_path = atlas.get_structures_path()
    registration_config = test_config_path

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

    assert (volumes_validate == volumes_test).all().all()
