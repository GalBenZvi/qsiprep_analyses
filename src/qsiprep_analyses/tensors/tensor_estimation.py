from pathlib import Path

from qsiprep_analyses.utils.data_grabber import DataGrabber


class TensorEstimation:
    def __init__(self, base_dir: Path) -> None:
        self.base_dir = Path(base_dir)
        self.data_grabber = DataGrabber(base_dir)
