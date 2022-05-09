import datetime
import logging
from pathlib import Path
from typing import List, Union

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
        derivatives = validate_instantiation(
            derivatives, base_dir, sessions_base, participant_label
        )
        super().__init__(derivatives)
        timestamp = datetime.datetime.today().strftime("%Y-%m-%d_%H%M%S")
        self.init_logger(
            name=self.LOGGER_FILE_FORMAT.format(
                name=__name__, timestamp=timestamp
            )
        )
        self.logger = logging.getLogger(__name__)

    def listify_sessions(self, sessions: Union[str, list]) -> List[str]:
        """
        Listifies *sessions* if it is not already a list.

        Parameters
        ----------
        sessions : Union[str,list]
            The sessions to be analyzed.

        Returns
        -------
        List[str]
            A list of sessions
        """
        if isinstance(sessions, str):
            sessions = [sessions]
        if isinstance(sessions, list) and all(
            [session in self.derivatives.sessions for session in sessions]
        ):
            return sessions
        else:
            return self.derivatives.sessions
