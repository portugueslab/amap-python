import os

import numpy as np
import nibabel as nb
from brainio import brainio
from neuro.atlas import Atlas

transpositions = {
    "horizontal": (1, 0, 2),
    "coronal": (2, 0, 1),
    "sagittal": (2, 1, 0),
}


class AtlasError(Exception):
    pass


class RegistrationAtlas(Atlas):
    """
    A class to handle all the atlas data (including the
    """

    def __init__(self, config_path, dest_folder=""):
        super().__init__(config_path)
        self.dest_folder = dest_folder

        self._pix_sizes = None  # cached to avoid reloading atlas
        self._atlas_data = None
        self._brain_data = None
        self._hemispheres_data = None

        if self["orientation"] != "horizontal":
            raise NotImplementedError(
                "Unknown orientation {}. Only horizontal supported so far".format(
                    self.original_orientation
                )
            )

    def load_all(self):
        for element in ["atlas", "brain", "hemispheres"]:
            attr_name = f"_{element}_data"
            if getattr(self, attr_name) is None:
                setattr(self, attr_name, self.get_nii_from_element(f"{element}_name"))

    def save_all(self):
        for element in ["atlas", "brain", "hemispheres"]:
            brainio.to_nii(getattr(self, f"_{element}_data"),
                           self.get_dest_path(f"{element}_name"))

    # FIXME: should be just changing the header
    def _flip(self, nii_img, axis_idx):
        return nb.Nifti1Image(
            np.flip(np.asanyarray(nii_img.dataobj), axis_idx),
            nii_img.affine,
            nii_img.header,
        )

    def _flip_all(self, axis_idx):
        self._atlas_data = self._flip(self._atlas_data, axis_idx)
        self._brain_data = self._flip(self._brain_data, axis_idx)
        self._hemispheres_data = self._flip(self._hemispheres_data, axis_idx)

    def flip(self, axes):
        for axis_idx, flip_axis in enumerate(axes):
            if flip_axis:
                self._flip_all(axis_idx)

    def _transpose(self, nii_img, transposition):
        # FIXME: should be just changing the header
        data = np.transpose(np.asanyarray(nii_img.dataobj), transposition)
        data = np.swapaxes(data, 0, 1)
        return nb.Nifti1Image(data, nii_img.affine, nii_img.header)

    def _transpose_all(self, transposition):
        self._atlas_data = self._transpose(self._atlas_data, transposition)
        self._brain_data = self._transpose(self._brain_data, transposition)
        self._hemispheres_data = self._transpose(
            self._hemispheres_data, transposition
        )

    def reorientate_to_sample(self, sample_orientation):
        self._transpose_all(transpositions[sample_orientation])

    def rotate(self, axes, k):
        self._rotate_all(axes, k)

    def _rotate_all(self, axes, k):
        self._atlas_data = self._rotate(self._atlas_data, axes, k)
        self._brain_data = self._rotate(self._brain_data, axes, k)
        self._hemispheres_data = self._rotate(self._hemispheres_data, axes, k)

    def _rotate(self, nii_img, axes, k):
        # FIXME: should be just changing the header
        data = np.rot90(np.asanyarray(nii_img.dataobj), axes=axes, k=k)
        # data = np.swapaxes(data, 0, 1)
        return nb.Nifti1Image(data, nii_img.affine, nii_img.header)

    def get_dest_path(self, atlas_element_name):
        if not self.dest_folder:
            raise AtlasError(
                "Could not get destination path. "
                "Missing destination folder information"
            )
        return str(self.dest_folder / self[atlas_element_name])

    def make_atlas_scale_transformation_matrix(self):
        scale = self.pix_sizes
        transformation_matrix = np.eye(4)
        for i, axis in enumerate(("x", "y", "z")):
            transformation_matrix[i, i] = scale[axis] / 1000
        return transformation_matrix

