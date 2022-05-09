"""
Definition of the :class:`TensorEstimation` class.
"""
import logging
from pathlib import Path
from typing import Callable, List, Union

from analyses_utils.entities.analysis.logger import get_console_handler
from analyses_utils.entities.derivatives.qsiprep import QsiprepDerivatives
from dipy.workflows.reconst import ReconstDkiFlow, ReconstDtiFlow

from qsiprep_analyses.data.bids import build_relative_path
from qsiprep_analyses.qsiprep_analysis import QsiprepAnalysis
from qsiprep_analyses.tensors.utils.functions import estimate_sigma
from qsiprep_analyses.tensors.utils.messages import (
    INVALID_OUTPUT,
    OUTPUTS_EXIST,
    RECONSTRUCTION_WORKFLOW,
    TENSOR_RECONSTRUCTION_NOT_IMPLEMENTED,
)
from qsiprep_analyses.tensors.utils.templates import (
    KWARGS_MAPPING,
    TENSOR_DERIVED_ENTITIES,
    TENSOR_DERIVED_METRICS,
)


class TensorEstimation(QsiprepAnalysis):
    #: Templates
    TENSOR_ENTITIES = TENSOR_DERIVED_ENTITIES.copy()
    METRICS = TENSOR_DERIVED_METRICS.copy()

    #: Tensor Workflows
    TENSOR_FITTING_KWARGS = KWARGS_MAPPING
    TENSOR_WORKFLOWS = {
        "diffusion_tensor": ReconstDtiFlow,
        "diffusion_kurtosis": ReconstDkiFlow,
        "restore_tensor": ReconstDtiFlow,
    }
    #: Tensor types
    TENSOR_TYPES = dict(
        diffusion_tensor={"acq": "dt", "kwargs": {"fit_method": "WLS"}},
        diffusion_kurtosis={"acq": "dk", "kwargs": {"fit_method": "WLS"}},
        restore_tensor={
            "acq": "rt",
            "kwargs": {"fit_method": "restore", "sigma": estimate_sigma},
        },
    )

    def __init__(
        self,
        derivatives: QsiprepDerivatives = None,
        base_dir: Union[Path, str] = None,
        participant_label: str = None,
        sessions_base: str = None,
    ):
        super().__init__(
            derivatives, base_dir, participant_label, sessions_base
        )
        self.logger = logging.getLogger(__name__)
        self.logger.addHandler(get_console_handler())

    def listify_tensor_type(self, tensor_types: Union[str, list]) -> List[str]:
        """
        Listifies *tensor_type* if it is not already a list.

        Parameters
        ----------
        tensor_types : Union[str,list]
            The tensor estimation method (either "dt", "rt" or "dk")

        Returns
        -------
        List[str]
            A list of tensor estimation methods
        """
        if isinstance(tensor_types, str):
            tensor_types = [tensor_types]
        if isinstance(tensor_types, list) and all(
            [self.validate_tensor_type(x, strict=False) for x in tensor_types]
        ):
            return tensor_types
        else:
            return self.TENSOR_TYPES.keys()

    def validate_tensor_type(
        self, tensor_type: str, strict: bool = True
    ) -> None:
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
            if strict:
                msg = TENSOR_RECONSTRUCTION_NOT_IMPLEMENTED.format(
                    tensor_type=tensor_type
                )
                self.logger.error(msg)
                raise NotImplementedError(msg)
            else:
                return False
        return True

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
            self.logger.warning(
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
        entities = {
            "acquisition": self.TENSOR_TYPES.get(tensor_type).get("acq"),
            **self.TENSOR_ENTITIES,
        }
        for output in outputs:
            if self.validate_requested_output(tensor_type, output):
                target[f"out_{output}"] = _gen_output_name(
                    output=output,
                    parent=self.derivatives.path.parent,
                    source=source,
                    entities=entities,
                )
        return target

    def get_inputs(self, session: str):
        """
        Returns the inputs for the tensor estimation workflow.

        Parameters
        ----------
        session : str
            The session to be analyzed.

        Returns
        -------
        dict
            A dictionary with keys of required inputs and their
            corresponding paths
        """
        inputs = {}
        for key, val in self.TENSOR_FITTING_KWARGS.items():
            inputs[val] = str(self.get_derivative(session, key))
        return inputs

    def format_reconstruction_message(
        self, tensor_type: str, session: str, kwargs: dict, outputs_exist: bool
    ) -> str:
        """
        Formats a tensor reconstruction message.

        Parameters
        ----------
        kwargs : dict
            The kwargs to be formatted

        Returns
        -------
        str
            The formatted message
        """
        parameters = dict(
            participant_label=str(self.derivatives.participant),
            session=session,
        )
        parameters.update(kwargs)
        if not outputs_exist:
            msg = RECONSTRUCTION_WORKFLOW.format(tensor_type=tensor_type)
        else:
            msg = OUTPUTS_EXIST.format(tensor_type=tensor_type)
        for key, val in kwargs.items():
            msg += f"\n{key}: {val}"
        return msg

    def run_tensor_workflow(
        self,
        session: str,
        tensor_type: str,
        outputs: List[str] = None,
        force: bool = False,
    ) -> None:
        """
        Run a tensor-fitting workflow for a given *tensor_type*.

        Parameters
        ----------
        session : str
            The session to run the workflow for
        tensor_type : str
            The tensor estimation method (either "dt" or "dk")
        outputs : List[str], optional
            Requested tensor-derived outputs, by default All available
        """
        if not self.validate_tensor_type(tensor_type):
            return
        inputs = self.get_inputs(session)
        outputs = self.build_output_dictionary(
            inputs.get("input_files"), tensor_type, outputs
        )
        kwargs = dict(
            **inputs, **outputs, **self.get_kwargs(inputs, tensor_type)
        )
        outputs_exist = [Path(val).exists() for val in outputs.values()]
        if all(outputs_exist):
            msg = self.format_reconstruction_message(
                tensor_type, session, kwargs, outputs_exist
            )
            self.logger.warning(msg)
            if not force:
                return outputs
        workflow = self.TENSOR_WORKFLOWS.get(tensor_type)()
        msg = self.format_reconstruction_message(
            tensor_type, session, kwargs, False
        )
        self.logger.info(msg)
        workflow.run(**kwargs)
        return outputs

    def get_kwargs(self, inputs: dict, tensor_type: str) -> dict:
        """
        Returns the kwargs for the tensor estimation workflow.

        Parameters
        ----------
        inputs : dict
            The inputs for the tensor estimation workflow.
        tensor_type : str
            The tensor estimation method (either "dt", "rt or "dk")

        Returns
        -------
        dict
            A dictionary with keys of required kwargs and their
            corresponding values
        """
        kwargs = {}
        for key, value in (
            self.TENSOR_TYPES.get(tensor_type).get("kwargs").items()
        ):
            if isinstance(value, Callable):
                kwargs[key] = value(inputs)
            else:
                kwargs[key] = value
        return kwargs

    def run(
        self,
        sessions: str = None,
        tensor_types: Union[str, list] = None,
        force: bool = True,
    ):
        """
        Run the tensor estimation workflow.

        Parameters
        ----------
        session : str, optional
            Specific session to run, by default All available
        tensor_type : str, optional
            The tensor estimation method (either "dt" or "dk") ,by default None
        force : bool, optional
             , by default True
        """
        tensor_types = self.listify_tensor_type(tensor_types)
        sessions = self.listify_sessions(sessions)
        output = {}

        for session in sessions:
            output[session] = {}
            for tensor_type in tensor_types:
                output[session][tensor_type] = self.run_tensor_workflow(
                    session, tensor_type, force=force
                )
        return output


def _gen_output_name(
    output: str,
    parent: Union[str, Path],
    source: Union[str, Path],
    entities: dict,
):
    output_parts = output.split("_")
    if len(output_parts) > 1:
        output_desc = "".join([output_parts[0], output_parts[1].capitalize()])
    else:
        output_desc = output
    return str(
        Path(parent)
        / build_relative_path(
            source,
            {"desc": output_desc, **entities},
        )
    )
