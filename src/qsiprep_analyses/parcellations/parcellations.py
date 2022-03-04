"""
Definition of the :class:`NativeParcellation` class.
"""
from pathlib import Path
from typing import Union

from qsiprep_analyses.utils.data_grabber import DataGrabber
from qsiprep_analyses.utils.utils import (
    collect_subjects,
    validate_instantiation,
)


class NativeParcellation:
    QUERIES = dict(
        mni2native_transform={
            "from": "MNI152NLin2009cAsym",
            "to": "T1w",
            "mode": "image",
            "suffix": "xfm",
        }
    )

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

    def get_transform(self, participant_label: str) -> list[str]:
        """
        Locates subject-specific transformation warp from standard (MNI) space to native.

        Parameters
        ----------
        participant_label : str
            Specific participants' labels to be queried

        Returns
        -------
        list[str]
            List of paths to MNI-to-native transforms (.h5)
        """
        query = dict(
            subject=participant_label,
            **self.QUERIES.get("mni2native_transform")
        )
        return self.data_grabber.layout.get(**query)
