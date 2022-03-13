"""
Definition of the :class:`NativeParcellation` class.
"""
from pathlib import Path
from typing import Tuple, Union

from qsiprep_analyses.utils.data_grabber import DataGrabber
from qsiprep_analyses.utils.utils import (
    collect_subjects,
    validate_instantiation,
)

# from brain_parts.parcellation.parcellations import (
#     Parcellation as parcellation_manager,
# )


class NativeParcellation:
    QUERIES = dict(
        mni2native={
            "from": "MNI152NLin2009cAsym",
            "to": "T1w",
            "mode": "image",
            "suffix": "xfm",
        },
        native2mni={
            "from": "T1w",
            "to": "MNI152NLin2009cAsym",
            "mode": "image",
            "suffix": "xfm",
        },
        anat_reference={
            "desc": "preproc",
            "suffix": "T1w",
            "datatype": "anat",
            "space": None,
            "extension": ".nii.gz",
        },
        dwi_reference={
            "desc": "preproc",
            "datatype": "dwi",
            "suffix": "dwi",
            "space": "T1w",
            "extension": ".nii.gz",
        },
        probseg={"suffix": "probseg"},
    )
    TRANSFORMS = ["mni2native", "native2mni"]

    def __init__(
        self,
        base_dir: Path = None,
        data_grabber: DataGrabber = None,
        participant_labels: Union[str, list] = None,
    ) -> None:
        self.data_grabber = validate_instantiation(
            self, base_dir, data_grabber
        )
        self.subjects = collect_subjects(self, participant_labels)

    def apply_bids_filters(self, original: dict, replacements: dict) -> dict:
        """
        Change an *original* bids-filters' query according to *replacements*

        Parameters
        ----------
        original : dict
            Original filters
        replacements : dict
            Replacement entities

        Returns
        -------
        dict
            Combined entities for bids query
        """
        combined_filters = original.copy()
        if isinstance(replacements, dict):
            for key, value in replacements.items():
                combined_filters[key] = value
        return combined_filters

    def get_transforms(
        self, participant_label: str, bids_filters: dict = None
    ) -> dict:
        """
        Locates subject-specific transformation warp from standard (MNI) space
        to native.

        Parameters
        ----------
        participant_label : str
            Specific participant's label to be queried

        Returns
        -------
        dict
            dictionary of paths to MNI-to-native
            and native-to-MNI transforms (.h5)
        """
        transforms = {}
        for transform in self.TRANSFORMS:

            query = dict(
                subject=participant_label, **self.QUERIES.get(transform)
            )
            query = self.apply_bids_filters(query, bids_filters)
            result = self.data_grabber.layout.get(**query)
            transforms[transform] = Path(result[0].path) if result else None
        return transforms

    def get_reference(
        self,
        participant_label: str,
        reference_type: str = "anat",
        bids_filters: dict = None,
    ) -> Path:
        """
        Locate a reference image

        Parameters
        ----------
        participant_label : str
            Specific participant's label to be queried
        reference_type : str, optional
            Any default available reference types, either "anat" or "dwi",
            by default "anat"
        space : str, optional
            Image's space, by default None
        session : str, optional
            Specific session to be queried, by default None

        Returns
        -------
        Path
            Path to the result reference image.
        """
        query = dict(
            subject=participant_label,
            **self.QUERIES.get(f"{reference_type}_reference"),
        )
        query = self.apply_bids_filters(query, bids_filters)
        result = self.data_grabber.layout.get(**query)
        return Path(result[0].path) if result else None

    def get_probseg(
        self,
        participant_label: str,
        tissue_type: str = "GM",
        bids_filters: dict = None,
    ) -> Path:
        """
        Locates subject's tissue probability segmentations

        Parameters
        ----------
        participant_label : str
            Specific participant's label to be queried
        tissue_type : str, optional
            Tissue to be queried, by default "GM"
        space : str, optional
            Image's space, by default None

        Returns
        -------
        Path
            Path to tissue probability segmentations image
        """
        query = dict(
            subject=participant_label,
            label=tissue_type.upper(),
            **self.QUERIES.get("probseg"),
        )
        query = self.apply_bids_filters(query, bids_filters)
        result = self.data_grabber.layout.get(**query)
        return Path(result[0].path) if result else None

    def initiate_subject(
        self, participant_label: str
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
        return [
            grabber(participant_label)
            for grabber in [
                self.get_transforms,
                self.get_reference,
                self.get_probseg,
            ]
        ]

    def register_parcellation_scheme(
        self,
        parcellation_scheme: str,
        participant_label: str,
        session: Union[str, list],
        crop_to_gm: bool = True,
        force: bool = False,
    ) -> dict:
        """_summary_

        Parameters
        ----------
        participant_label : str
            _description_
        session : Union[str,list]
            _description_
        crop_to_gm : bool, optional
            _description_, by default True
        force : bool, optional
            _description_, by default False

        Returns
        -------
        dict
            _description_
        """
        transforms, anatomical_reference, gm_probseg = self.initiate_subject(
            participant_label
        )
