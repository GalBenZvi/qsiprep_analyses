"""
Definition of the :class:`NativeParcellation` class.
"""
from pathlib import Path
from typing import Union

from qsiprep_analyses.utils.data_grabber import DataGrabber
from qsiprep_analyses.utils.utils import validate_instantiation


class NativeParcellation:
    def __init__(
        self,
        base_dir: Path = None,
        data_grabber: DataGrabber = None,
        participant_labels: Union[str, list] = None,
    ) -> None:
        self.data_grabber = validate_instantiation(
            self, base_dir, data_grabber
        )

    def validate_instansiation(
        self, base_dir: Path = None, data_grabber: DataGrabber = None
    ) -> DataGrabber:
        """
        Validates the instansitation of *NativeParcellation* object with base directory or DataGrabber instance.

        Parameters
        ----------
        base_dir : Path, optional
            A base directory of *qsiprep*'s derivatives, by default None
        data_grabber : DataGrabber, optional
            A DataGrabber instance, already instansiated with a *base_dir*, by default None

        Returns
        -------
        DataGrabber
            An instansiated DataGrabber
        """
        if isinstance(data_grabber, DataGrabber):
            return data_grabber
        if base_dir:
            return DataGrabber(base_dir)
        raise ValueError(MISSING_DATAGRABBER)
