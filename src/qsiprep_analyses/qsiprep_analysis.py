from pathlib import Path
from typing import Union

from analyses_utils.entities.analysis.analysis import Analysis
from analyses_utils.entities.derivatives.qsiprep import QsiprepDerivatives

from qsiprep_analyses.utils.utils import validate_instantiation


class QsiprepAnalysis(Analysis):
    def __init__(
        self,
        derivatives: QsiprepDerivatives = None,
        base_dir: Union[Path, str] = None,
        participant_label: str = None,
        sessions_base: str = None,
    ):
        """
        Initializes the QsiprepAnalysis class.

        Parameters
        ----------
        derivatives : QsiprepDerivatives, optional
            An intansiated QsiprepDerivatives object , by default None
        base_dir : Union[Path, str], optional
            Base directory to be used for
            Participant object instansiation , by default None
        participant_label : str, optional
            Participant's label , by default None
        sessions_base : str, optional
            Where to look for available sessions
            under participant's label , by default None
        """
        self.derivatives = validate_instantiation(
            derivatives, base_dir, sessions_base, participant_label
        )
