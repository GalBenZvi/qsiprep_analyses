from pathlib import Path
from typing import Union

from qsiprep_analyses.utils.data_grabber import DataGrabber
from qsiprep_analyses.utils.utils import (
    collect_subjects,
    validate_instantiation,
)


class QsiprepManager:
    def __init__(
        self,
        base_dir: Path,
        data_grabber: DataGrabber = None,
        participant_labels: Union[str, list] = None,
    ) -> None:
        self.data_grabber = validate_instantiation(
            self, base_dir, data_grabber
        )
        self.subjects = collect_subjects(self, participant_labels)
