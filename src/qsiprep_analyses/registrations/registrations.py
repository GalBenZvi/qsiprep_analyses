"""
Definition of the :class:`NativeRegistration` class.
"""
import logging
from pathlib import Path
from typing import Tuple, Union

import nibabel as nib
from analyses_utils.entities.analysis.logger import get_console_handler
from analyses_utils.entities.derivatives.qsiprep import QsiprepDerivatives
from brain_parts.parcellation.parcellations import (
    Parcellation as parcellation_manager,
)
from nilearn.image.resampling import resample_to_img

from qsiprep_analyses.data.bids import build_relative_path
from qsiprep_analyses.qsiprep_analysis import QsiprepAnalysis
from qsiprep_analyses.registrations.utils import (
    ANAT_REG_KEYS,
    DEFAULT_PARCELLATION_NAMING,
    PROBSEG_THRESHOLD,
    QUERIES,
    TRANSFORMS,
)


class NativeRegistration(QsiprepAnalysis):
    #: Queries
    QUERIES = QUERIES
    #: Naming
    DEFAULT_PARCELLATION_NAMING = DEFAULT_PARCELLATION_NAMING

    #: Types of transformations
    TRANSFORMS = TRANSFORMS

    #: Default probability segmentations' threshold
    PROBSEG_THRESHOLD = PROBSEG_THRESHOLD

    def __init__(
        self,
        derivatives: QsiprepDerivatives = None,
        base_dir: Union[Path, str] = None,
        participant_label: str = None,
        sessions_base: str = None,
    ):
        super().__init__(
            derivatives, base_dir, participant_label, sessions_base
        )
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(get_console_handler())
        self.parcellation_manager = parcellation_manager(logger=self.logger)

    def collect_requirements(
        self,
    ) -> Tuple[dict, Path, Path]:
        """
        Query initially-required patricipant's files

        Parameters
        ----------
        participant_label : str
            Specific participant's label to be queried

        Returns
        -------
        Tuple[dict,Path,Path]
            A tuple of required files for parcellation registration.
        """
        self.logger.info(
            f"Initiating registration process for participant sub-{self.participant_label}"  # noqa
        )
        return [
            self.get_derivative(**QUERIES.get(key)) for key in ANAT_REG_KEYS
        ]

    def build_output_dictionary(
        self, parcellation_scheme: str, reference: Path, resolution: str
    ) -> dict:
        """
        Based on a *reference* image,
        reconstruct output names for native parcellation naming.

        Parameters
        ----------
        reference : Path
            The reference image.
        resolution : str
            The reference image type (either "anat" or "dwi")

        Returns
        -------
        dict
            A dictionary with keys of "whole-brain" and "gm-cropped" and their
            corresponding paths
        """
        basic_query = dict(
            atlas=parcellation_scheme,
            resolution=resolution,
            **self.DEFAULT_PARCELLATION_NAMING,
        )
        outputs = dict()
        for key, label in zip(
            ["whole_brain", "gm_cropped"], ["WholeBrain", "GM"]
        ):
            query = basic_query.copy()
            query["label"] = label
            outputs[key] = self.derivatives.path.parent / build_relative_path(
                reference, query
            )
        return outputs

    def register_to_anatomical(
        self,
        parcellation_scheme: str,
        probseg_threshold: float = None,
        force: bool = False,
    ) -> dict:
        """
        Register a *parcellation scheme* from standard to native anatomical space. # noqa

        Parameters
        ----------
        parcellation_scheme : str
            A string representing existing key within *self.parcellation_manager.parcellations*.
        participant_label : str
            Specific participant's label
        probseg_threshold : float, optional
            Threshold for probability segmentation masking, by default None
        force : bool, optional
            Whether to re-write existing files, by default False

        Returns
        -------
        dict
            A dictionary with keys of "whole_brain" and "gm_cropped" native-spaced parcellation schemes.
        """
        mni2native, reference, gm_probseg = self.collect_requirements()
        whole_brain, gm_cropped = [
            self.build_output_dictionary(
                parcellation_scheme, reference, resolution="anat"
            ).get(key)
            for key in ["whole_brain", "gm_cropped"]
        ]
        self.parcellation_manager.register_parcellation_scheme(
            parcellation_scheme,
            self.participant_label,
            reference,
            mni2native,
            whole_brain,
            force=force,
        )
        self.parcellation_manager.crop_to_probseg(
            parcellation_scheme,
            self.participant_label,
            whole_brain,
            gm_probseg,
            gm_cropped,
            masking_threshold=probseg_threshold or self.PROBSEG_THRESHOLD,
            force=force,
        )
        return whole_brain, gm_cropped

    def register_dwi(
        self,
        parcellation_scheme: str,
        session: str,
        anatomical_whole_brain: Path,
        anatomical_gm_cropped: Path,
        force: bool = False,
    ):
        """
        Resample parcellation scheme from anatomical to DWI space.

        Parameters
        ----------
        parcellation_scheme : str
            A string representing existing key within *self.parcellation_manager.parcellations*. # noqa
        participant_label : str
            Specific participant's label
        anatomical_whole_brain : Path
            Participant's whole-brain parcellation scheme in anatomical space
        anatomical_gm_cropped : Path
            Participant's GM-cropped parcellation scheme in anatomical space
        force : bool, optional
            Whether to re-write existing files, by default False
        """
        self.logger.info("Resampling parcellation scheme to DWI space")
        reference = self.get_derivative(session, "coreg_dwi_image")
        if not reference:
            raise FileNotFoundError(
                f"Could not find DWI reference file for subject {self.participant_label}!"  # noqa
            )
        whole_brain, gm_cropped = [
            self.build_output_dictionary(
                parcellation_scheme, reference, "dwi"
            ).get(key)
            for key in ["whole_brain", "gm_cropped"]
        ]
        for source, target in zip(
            [anatomical_whole_brain, anatomical_gm_cropped],
            [whole_brain, gm_cropped],
        ):
            if not target.exists() or force:
                img = resample_to_img(
                    str(source), str(reference), interpolation="nearest"
                )
                nib.save(img, target)

        return whole_brain, gm_cropped

    def run(
        self,
        parcellation_scheme: str,
        session: Union[str, list] = None,
        probseg_threshold: float = None,
        force: bool = False,
    ) -> dict:
        """


        Parameters
        ----------
        parcellation_scheme : str
            A string representing existing key within *self.parcellation_manager.parcellations*. # noqa
        participant_label : str
            Specific participant's label
        session : Union[str, list], optional
            Specific sessions available for *participant_label*, by default None # noqa
        probseg_threshold : float, optional
            Threshold for probability segmentation masking, by default None
        force : bool, optional
            Whether to re-write existing files, by default False

        Returns
        -------
        dict
            A dictionary with keys of "anat" and available or requested sessions,
            and corresponding natice parcellations as keys.
        """
        outputs = {}
        anat_whole_brain, anat_gm_cropped = self.register_to_anatomical(
            parcellation_scheme, probseg_threshold, force
        )
        outputs["anat"] = {
            "whole_brain": anat_whole_brain,
            "gm_cropped": anat_gm_cropped,
        }
        for session in self.listify_sessions(session):
            whole_brain, gm_cropped = self.register_dwi(
                parcellation_scheme,
                session,
                anat_whole_brain,
                anat_gm_cropped,
                force,
            )
            outputs[session] = {
                "whole_brain": whole_brain,
                "gm_cropped": gm_cropped,
            }
        return outputs
