"""
Definition of the :class:`NativeParcellation` class.
"""
from pathlib import Path
from typing import List, Union

import pandas as pd
from brain_parts.parcellation.parcellations import (
    Parcellation as parcellation_manager,
)

from qsiprep_analyses.manager import QsiprepManager
from qsiprep_analyses.registrations.registrations import NativeRegistration
from qsiprep_analyses.tensors.tensor_estimation import TensorEstimation


class NativeParcellation(QsiprepManager):
    def __init__(
        self,
        base_dir: Path,
        participant_labels: Union[str, list] = None,
    ) -> None:
        super().__init__(base_dir, participant_labels)
        self.registration_manager = NativeRegistration(
            base_dir, participant_labels
        )
        self.parcellation_manager = parcellation_manager()
        self.tensor_estimation = TensorEstimation(base_dir, participant_labels)

    def generate_rows(
        self, participant_label: str, session: Union[str, list]
    ) -> pd.MultiIndex:
        """
        Generate target DataFrame's multiindex for participant's rows.

        Parameters
        ----------
        participant_label : str
            Specific participants' labels
        session : Union[str, list]
            Specific session(s)' labels

        Returns
        -------
        pd.MultiIndex
            A MultiIndex comprised of participant's label
            and its corresponding sessions.
        """
        if session:
            if isinstance(session, str):
                sessions = [session]
            elif isinstance(session, str):
                sessions = session
        else:
            sessions = self.subjects.get(participant_label)
        return pd.MultiIndex.from_product([[participant_label], sessions])

    def generate_columns(
        self,
        parcellation_scheme: str,
        tensor_type: str,
        index_columns: Union[str, list] = ["index"],
        metrics: List[str] = None,
    ) -> pd.MultiIndex:
        """_summary_

        Parameters
        ----------
        parcellation_scheme : str
            _description_
        tensor_type : str
            _description_
        index_columns : Union[str, list], optional
            _description_, by default ["index"]
        metrics : List[str], optional
            _description_, by default None

        Returns
        -------
        pd.MultiIndex
            _description_
        """
        tensor_type = self.tensor_estimation.validate_tensor_type()
        # parcels = self.parcellation_manager.parcellations.get(
        #     parcellation_scheme
        # ).get("parcels")
        if metrics:
            if isinstance(metrics, str):
                metrics = [metrics]
        else:
            metrics = self.tensor_estimation.METRICS.get(tensor_type)
