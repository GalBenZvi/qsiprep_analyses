from pathlib import Path

from qsiprep_analyses.parcellations.messages import MISSING_DATAGRABBER
from qsiprep_analyses.utils.data_grabber import DataGrabber


def validate_instantiation(
    instance: object,
    base_dir: Path = None,
    data_grabber: DataGrabber = None,
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
    raise ValueError(MISSING_DATAGRABBER.format(object_name=instance.__name__))
