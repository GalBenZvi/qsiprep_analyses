"""
Definition of the :class:`TensorEstimation` class.
"""
import warnings
from pathlib import Path
from typing import List, Tuple, Union

from dipy.workflows.reconst import ReconstDkiFlow, ReconstDtiFlow

from qsiprep_analyses.tensors.utils import (DWI_ENTITIES, KWARGS_MAPPING,
                                            RECONSTRUCTION_COMMANDS,
                                            TENSOR_DERIVED_ENTITIES,
                                            TENSOR_DERIVED_METRICS)
from qsiprep_analyses.utils.data_grabber import DataGrabber

warnings.simplefilter("default", Warning)


class TensorEstimation:
    #: Templates
    DWI_QUERY_ENTITIES = DWI_ENTITIES.copy()
    TENSOR_ENTITIES = TENSOR_DERIVED_ENTITIES.copy()
    METRICS = TENSOR_DERIVED_METRICS.copy()
    TENSOR_RECONSTRUCTION_COMMANDS = RECONSTRUCTION_COMMANDS.copy()

    #: Tensor Workflows
    TENSOR_FITTING_KWARGS = KWARGS_MAPPING
    TENSOR_WORKFLOWS = {"dt": ReconstDtiFlow, "dk": ReconstDkiFlow}
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
        Queries available sessions for *participant_labels*.

        Parameters
        ----------
        participant_labels : Union[str, List], optional
            Specific participants' labels to be queried, by default None

        Returns
        -------
        dict
            A dictionary with participant labels as keys and available
             sessions as values
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
        Locate subject's available preprocessed DWIs and their corresponding
        gradients (.bvec and .bval).

        Parameters
        ----------
        participant_label : str
            Specific participants' labels to be queried
        session : str, optional
            Specific session's ID, by default None

        Returns
        -------
        List[dict]
            A list of dictionary with keys of ["dwi","bvec","bval"] for all
            available DWIs
        """
        query = dict(
            subject=participant_label,
            **self.DWI_QUERY_ENTITIES,
        )
        if session:
            query["session"] = session
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

    def validate_tensor_type(self, tensor_type: str) -> None:
        """
        Validates *tensor_type* as an implemented tensor estimation protocol.

        Parameters
        ----------
        tensor_type : str
            The tensor estimation method (either "dt" or "dk")

        Raises
        ------
        NotImplementedError
            In case *tensor_type* is not an implemented key of recognized
            tensor-estimation protocol
        """
        if tensor_type not in self.TENSOR_TYPES:
            message = f"Estimation of {tensor_type}-derived metrics is not yet implemented."  # noqa: E501
            raise NotImplementedError(message)

    def validate_requested_output(self, tensor_type: str, output: str) -> bool:
        """
        Validates a requested output to be a valid *tensor_type* derived metric

        Parameters
        ----------
        tensor_type : str
            The tensor estimation method (either "dt" or "dk")
        output : str
            The requested output

        Returns
        -------
        bool
            Whether the requested *output* is a valid output of *tensor_type*
            derived metrics
        """
        if output in self.METRICS.get(tensor_type):
            return True
        else:
            warnings.warn(
                f"""Requested output {output} is not a valid ({tensor_type}) tensor-derived metric.
            Available metrics are: {', '.join(self.METRICS.get(tensor_type))}"""  # noqa: E501
            )
            return False

    def build_output_dictionary(
        self, source: Path, tensor_type: str, outputs: List[str] = None
    ) -> dict:
        """
        Based on a *source* DWI, reconstruct output names for tensor-derived
        metric available under *tensor_type*.

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
            A dictionary with keys of available/requested outputs and their
            corresponding paths
        """
        self.validate_tensor_type(tensor_type)
        outputs = outputs or self.METRICS.get(tensor_type)
        return {
            f"out_{output}": str(
                self.data_grabber.build_path(
                    source,
                    {
                        "acquisition": tensor_type,
                        "desc": output,
                        **self.TENSOR_ENTITIES,
                    },
                )
            )
            for output in outputs
            if self.validate_requested_output(tensor_type, output)
        }

    def map_kwargs_to_workflow(self, inputs: dict) -> dict:
        """
        Maps inputs' dictionary's keys to their corresponding kwargs in
        relevant Workflows.

        Parameters
        ----------
        inputs : dict
            A dictionary with keys of inputs and values of their corresponding
            paths

        Returns
        -------
        dict
            The same dictionary with keys that match workflows' kwargs
        """
        workflow_kwargs = {}
        for key, val in inputs.items():
            kwarg = self.TENSOR_FITTING_KWARGS.get(key) or key
            workflow_kwargs[kwarg] = str(val)
        return workflow_kwargs

    def validate_single_subject_run(
        self,
        participant_label: str,
        session: Union[List, str] = None,
        tensor_type: Union[List, str] = None,
        out_metrics: Union[List, str] = None,
    ) -> Tuple[List, List, List]:
        """
        Validates the requested single-subject run's properties

        Parameters
        ----------
        participant_label : str
            Specific participants' labels to be queried
        session : Union[List, str], optional
            Specific session's ID, by default None
        tensor_type : Union[List, str], optional
            The tensor estimation method (either "dt" or "dk")
        out_metrics : Union[List, str], optional
            Requested tensor-derived outputs, by default All available, by
            default None

        Returns
        -------
        Tuple[List, List, List]
            Validated tensor estimation protocol, sessions and output metrics
        """
        tensor_types = tensor_type or self.TENSOR_TYPES
        if isinstance(tensor_type, str):
            tensor_types = [tensor_type]
        sessions = session or self.subjects.get(participant_label)
        if isinstance(sessions, str):
            sessions = [sessions]
        if isinstance(out_metrics, str):
            out_metrics = [out_metrics]
        return tensor_types, sessions, out_metrics

    def run_single_input(
        self,
        inputs: dict,
        tensor_type: str,
        out_metrics: list = None,
        force: bool = False,
    ) -> dict:
        """
        Runs a single input set (DWI and its corresponding files)

        Parameters
        ----------
        inputs : dict
            A dictionary with keys of ["dwi","bval","bvec","mask"]
        tensor_type : str
            The tensor estimation method (either "dt" or "dk")
        out_metrics : list
            Requested tensor-derived outputs, by default All available, by
            default None
        force : bool
            Whether to force the creation of outputs (rather than keeping
            pre-existing ones), by default False

        Returns
        -------
        dict
            Dictionary with requested outputs as keys and their corresponding
            generated files' paths as values.
        """

        self.validate_tensor_type(tensor_type)
        outputs = self.build_output_dictionary(
            inputs.get("dwi"), tensor_type, out_metrics
        )
        workflow_kwargs = self.map_kwargs_to_workflow(inputs)
        wf = self.TENSOR_WORKFLOWS.get(tensor_type)
        runner = wf(force=force)
        runner.run(**workflow_kwargs, **outputs)

        return outputs

    def run_single_session(
        self,
        participant_label: str,
        session: str,
        tensor_types: list,
        out_metrics: list = None,
        force: bool = False,
    ) -> dict:
        """
        Locates session-specific DWI-related files and estimates their
        tensor-derived metrics.

        Parameters
        ----------
        participant_label : str
            Specific participants' labels to be analyzed
        session : str
            Specific session's ID
        tensor_types : list
            The tensor estimation method(s) (either "dt" or "dk")
        out_metrics : list
            Requested tensor-derived outputs, by default All available, by
            default None
        force : bool
            Whether to force the creation of outputs (rather than keeping
            pre-existing ones), by default False

        Returns
        -------
        dict
            A dictionary with *tensor_types* as keys and a list of
            tensor-derived metrics as values
        """
        dwis = self.get_subject_dwi(participant_label, session)
        result = {}
        for tensor_type in tensor_types:
            result[tensor_type] = []
            for inputs in dwis:
                outputs = self.run_single_input(
                    inputs, tensor_type, out_metrics, force
                )
                result[tensor_type].append(outputs)
        return result

    def run_single_subject(
        self,
        participant_label: str,
        session: Union[List, str] = None,
        tensor_type: Union[List, str] = None,
        out_metrics: Union[List, str] = None,
        force: bool = False,
    ) -> dict:
        """
        Run tensor-derived metrics' estimation for all available DWIs under
        *participant_label*.

        Parameters
        ----------
        participant_label : str
            Specific participants' labels to be queried
        session : Union[List, str], optional
            Specific session's ID, by default None
        tensor_type : Union[List, str], optional
            The tensor estimation method (either "dt" or "dk")
        out_metrics : Union[List, str], optional
            Requested tensor-derived outputs, by default All available, by
            default None
        force : bool
            Whether to force the creation of outputs (rather than keeping
            pre-existing ones), by default False

        Returns
        -------
        dict
            A nested dictionary with sessions as keys and a dictionary for
            each *tensor_type* as values
        """
        tensor_types, sessions, out_metrics = self.validate_single_subject_run(
            participant_label, session, tensor_type, out_metrics
        )
        result = {}
        for session in sessions:
            result[session] = self.run_single_session(
                participant_label, session, tensor_types, out_metrics, force
            )
        return result
