"""
Definition of the :class:`TensorEstimation` class.
"""
import os
import warnings
from pathlib import Path
from typing import List, Tuple, Union

import tqdm
from dmriprep_analyses.manager import DmriprepManager
from dmriprep_analyses.tensors.messages import (
    INVALID_OUTPUT,
    INVALID_PARTICIPANT,
    TENSOR_RECONSTRUCTION_NOT_IMPLEMENTED,
)
from dmriprep_analyses.tensors.utils import (
    DWI_ENTITIES,
    KWARGS_MAPPING,
    TENSOR_DERIVED_ENTITIES,
    TENSOR_DERIVED_METRICS,
    build_tensor_fitting_cmd,
)


class TensorEstimation(DmriprepManager):
    #: Templates
    DWI_QUERY_ENTITIES = DWI_ENTITIES.copy()
    TENSOR_ENTITIES = TENSOR_DERIVED_ENTITIES.copy()
    METRICS = TENSOR_DERIVED_METRICS.copy()

    #: Tensor Workflows
    TENSOR_FITTING_KWARGS = KWARGS_MAPPING
    #: Tensor types
    TENSOR_TYPES = dict(
        diffusion_tensor={"acq": "dt", "fit_method": "WLS"},
    )

    def __init__(
        self,
        base_dir: Path,
        participant_labels: Union[str, list] = None,
    ) -> None:
        super().__init__(base_dir, participant_labels)

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
            raise NotImplementedError(
                TENSOR_RECONSTRUCTION_NOT_IMPLEMENTED.format(
                    tensor_type=tensor_type
                )
            )
        return self.TENSOR_TYPES.get(tensor_type)

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
                INVALID_OUTPUT.format(
                    output=output,
                    tensor_type=tensor_type,
                    available_metrics=", ".join(self.METRICS.get(tensor_type)),
                )
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
        outputs = outputs or self.METRICS.get(tensor_type)
        target = {}
        for output, output_desc in outputs.items():
            if self.validate_requested_output(tensor_type, output):
                target[output] = str(
                    self.data_grabber.build_path(
                        source,
                        {
                            "acquisition": self.TENSOR_TYPES.get(
                                tensor_type
                            ).get("acq"),
                            "desc": output_desc,
                            **self.TENSOR_ENTITIES,
                        },
                    )
                )

        return target

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
        if participant_label not in self.subjects:
            raise ValueError(
                INVALID_PARTICIPANT.format(
                    base_dir=self.data_grabber.base_dir,
                    participant_label=participant_label,
                )
            )
        tensor_types = tensor_type or list(self.TENSOR_TYPES.keys())
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

        tensor_kwargs = self.validate_tensor_type(tensor_type)
        outputs = self.build_output_dictionary(
            inputs.get("dwi"),
            tensor_type,
            out_metrics,
        )
        workflow_kwargs = self.map_kwargs_to_workflow(inputs)
        if "fit_method" in tensor_kwargs:
            workflow_kwargs["fit_method"] = tensor_kwargs.get("fit_method")
        outputs_exist = [Path(val).exists() for val in outputs.values()]
        if (not all(outputs_exist)) or (force):
            with warnings.catch_warnings():
                warnings.filterwarnings("ignore")
                runner = build_tensor_fitting_cmd(workflow_kwargs, outputs)
                os.system(runner)

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
        dwis = self.get_subject_dwi(
            participant_label, session, queries=self.DWI_QUERY_ENTITIES
        )
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

    def run_dataset(
        self,
        participant_label: Union[str, list] = None,
        tensor_type: Union[List, str] = None,
        out_metrics: Union[List, str] = None,
        force: bool = False,
    ) -> dict:
        """
        Run tensor estimation for an entire dataset

        Parameters
        ----------
        participant_label : Union[str, list], optional
            Specific subject/s within the dataset to run, by default None
        tensor_type : Union[List, str], optional
            Type of tensor estimation to perform, by default All implemented
        out_metrics : Union[List, str], optional
            Specific metric of the tensor to produce, by default All
        force : bool, optional
            Whether to remove existing products and generate new ones, by default False # noqa

        Returns
        -------
        dict
            Dictionary with keys of subjects and values of session-wise tensor estimation's products
        """
        tensor_metrics = {}
        if participant_label:
            if isinstance(participant_label, str):
                participant_labels = [participant_label]
            elif isinstance(participant_label, list):
                participant_labels = [participant_label]
        else:
            participant_labels = list(self.subjects.keys())
        for participant_label in tqdm.tqdm(participant_labels):
            try:
                sessions = self.subjects.get(participant_label)
                tensor_metrics[participant_label] = self.run_single_subject(
                    participant_label=participant_label,
                    session=sessions,
                    tensor_type=tensor_type,
                    out_metrics=out_metrics,
                    force=force,
                )
            except TypeError:
                continue
