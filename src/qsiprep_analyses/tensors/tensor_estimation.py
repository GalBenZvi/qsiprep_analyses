from pathlib import Path
from typing import List, Union

from qsiprep_analyses.tensors.utils import (
    DWI_ENTITIES,
    TENSOR_DERIVED_ENTITIES,
    TENSOR_DERIVED_METRICS,
)
from qsiprep_analyses.utils.data_grabber import DataGrabber


class TensorEstimation:
    #: Templates
    DWI_QUERY_ENTITIES = DWI_ENTITIES.copy()
    TENSOR_ENTITIES = TENSOR_DERIVED_ENTITIES.copy()
    METRICS = TENSOR_DERIVED_METRICS.copy()

    #: Tensor types
    TENSOR_TYPES = ["dt", "dk"]

    def __init__(
        self,
        data_grabber: DataGrabber = None,
        participant_labels: Union[str, List] = None,
    ) -> None:
        if data_grabber:
            self.data_grabber = data_grabber
        self.subjects = self.get_subjects(participant_labels)

    def get_subjects(
        self,
        participant_labels: Union[str, List] = None,
    ) -> dict:
        """
        Queries available sessions for *participant_labels*

        Parameters
        ----------
        participant_labels : Union[str, List], optional
            Specific participants' labels to be queried, by default None

        Returns
        -------
        dict
            A dictionary with participant labels as keys and available sessions as values
        """
        if not participant_labels:
            return self.data_grabber.subjects

        if isinstance(participant_labels, str):
            participant_labels = [participant_labels]
        return {
            participant_label: self.data_grabber.subjects.get(
                participant_label
            )
            for participant_label in participant_labels
        }

    def get_subject_dwi(
        self, participant_label: str, session: str = None
    ) -> List[dict]:
        """
        Locate subject's available preprocessed DWIs and their corresponding gradients (.bvec and .bval)

        Parameters
        ----------
        participant_label : str
            Specific participants' labels to be queried
        session : str, optional
            Specific session's ID, by default None

        Returns
        -------
        List[dict]
            A list of dictionary with keys of ["dwi","bvec","bval"] for all available DWIs
        """
        query = dict(
            subject=participant_label,
            **self.DWI_QUERY_ENTITIES,
        )
        if session:
            query["session"] = (session,)
        dwi_files = self.data_grabber.layout.get(**query, return_type="file")
        result = []
        for dwi in dwi_files:
            result.append(
                {
                    "dwi": dwi,
                    "bval": self.data_grabber.layout.get_bval(dwi),
                    "bvec": self.data_grabber.layout.get_bvec(dwi),
                    "mask": self.data_grabber.build_path(
                        dwi, {"desc": "brain", "suffix": "mask"}
                    ),
                }
            )
        return result

    def built_output_dictionary(
        self, source: Path, tensor_type: str, outputs: list = None
    ) -> dict:
        """
        Based on a *source* DWI, reconstruct output names for tensor-derived metric available under *tensor_type*

        Parameters
        ----------
        source : Path
            The source DWI file.
        tensor_type : str
            The tensor estimation method (either "dt" or "dk")
        outputs : list, optional
            Requested tensor-derived outputs, by default All available

        Returns
        -------
        dict
            A dictionary with keys of available/requested outputs and their corresponding paths.
        """
        if tensor_type not in self.TENSOR_TYPES:
            raise NotImplementedError(
                f"Estimation of {tensor_type}-derived metrics is not yet implemented."
            )
        outputs = outputs or self.METRICS.get(tensor_type)
        return {
            f"out_{output}": self.data_grabber.build_path(
                source,
                {
                    "acquisition": tensor_type,
                    "desc": output,
                    **self.TENSOR_ENTITIES,
                },
            )
            for output in outputs
        }
