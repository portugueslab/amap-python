import pytest
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

TEST_ATLAS = "allen_2017_100um"


def download_atlas(directory):
    download_args = [
        "amap_download",
        "--atlas",
        TEST_ATLAS,
        "--install-path",
        directory,
        "--no-amend-config",
    ]
    sys.argv = download_args
    amap_download()
    return directory


def generate_test_config(atlas_dir):
    config = os.path.join(os.getcwd(), "tests", "data", "config", "test.conf")
    config_obj = get_config_obj(config)
    atlas_conf = config_obj["atlas"]
    orig_base_directory = atlas_conf["base_folder"]

    with open(config, "r") as in_conf:
        data = in_conf.readlines()
    for i, line in enumerate(data):
        data[i] = line.replace(
            f"base_folder = '{orig_base_directory}",
            f"base_folder = '{os.path.join(atlas_dir, TEST_ATLAS)}",
        )
    test_config = os.path.join(atlas_dir, "config.conf")
    with open(test_config, "w") as out_conf:
        out_conf.writelines(data)

    return test_config


@pytest.fixture()
def test_config_path(tmpdir):
    print("fixture")
    atlas_directory = str(tmpdir)
    download_atlas(atlas_directory)
    test_config = generate_test_config(atlas_directory)
    return test_config
