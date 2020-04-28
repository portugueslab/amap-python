import os
from pathlib import Path
import sys
import pytest

import pandas as pd

from brainio.brainio import load_nii
from imlib.general.string import get_text_lines

from imlib.general.config import get_config_obj
from amap.download.cli import main as amap_download
from amap.cli import run as amap_run

data_dir = os.path.join(os.getcwd(), "tests", "data", "brain",)
test_output_dir = os.path.join(
    os.getcwd(), "tests", "data", "registration_output",
)

x_pix = "40"
y_pix = "40"
z_pix = "50"




#@pytest.mark.slow
def test_register(tmpdir, test_config_path):

    output_directory = os.path.join(str(tmpdir), "output")
    amap_args = [
        "amap",
        data_dir,
        output_directory,
        "-x",
        x_pix,
        "-y",
        y_pix,
        "-z",
        z_pix,
        "--n-free-cpus",
        "0",
        "--registration-config",
        test_config_path,
        "-d",
        data_dir,
    ]

    sys.argv = amap_args
    amap_run()

    image_list = [
        "annotations.nii",
        "boundaries.nii",
        "brain_filtered.nii",
        "control_point_file.nii",
        "downsampled.nii",
        "hemispheres.nii",
        "inverse_control_point_file.nii",
        "registered_atlas.nii",
        "registered_hemispheres.nii",
        "downsampled_brain.nii",
    ]

    for image in image_list:
        are_images_equal(image, output_directory, test_output_dir)

    assert get_text_lines(
        os.path.join(output_directory, "affine_matrix.txt")
    ) == get_text_lines(os.path.join(test_output_dir, "affine_matrix.txt"))

    assert get_text_lines(
        os.path.join(output_directory, "invert_affine_matrix.txt")
    ) == get_text_lines(
        os.path.join(test_output_dir, "invert_affine_matrix.txt")
    )

    assert (
        (
            pd.read_csv(os.path.join(output_directory, "volumes.csv"))
            == pd.read_csv(os.path.join(test_output_dir, "volumes.csv"))
        )
        .all()
        .all()
    )


def are_images_equal(image_name, output_directory, test_output_directory):
    image = load_nii(os.path.join(output_directory, image_name), as_array=True)
    test_image = load_nii(
        os.path.join(test_output_directory, image_name), as_array=True
    )

    assert (image == test_image).all()
