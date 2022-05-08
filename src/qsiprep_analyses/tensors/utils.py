from pathlib import Path
from typing import Union

from bids.layout import parse_file_entities
from bids.layout.writing import build_path

from qsiprep_analyses.data.bids import DEFAULT_PATTERNS


def build_relative_path(
    source: Union[Path, str],
    replacements: dict,
    path_patterns: list = DEFAULT_PATTERNS,
) -> Path:
    """
    Build a BIDS-compatible path according to source file/entities.

    Parameters
    ----------
    source : Union[Path,str]
        Either a source file (to be parsed to entities) or its BIDS
    replacements : dict
        A dictionary with keys as entities and values as

    Returns
    -------
    Path
        Path to BIDS-compatible path
    """
    source_entities = parse_file_entities(source)

    for key, value in replacements.items():
        source_entities[key] = value
    return build_path(
        source_entities, path_patterns=path_patterns, strict=False
    )


TENSOR_DERIVED_ENTITIES = dict(suffix="dwiref", resolution="dwi")

TENSOR_DERIVED_METRICS = dict(
    diffusion_tensor=dict(
        fa="fa",
        adc="md",
        ad="ad",
        rd="rd",
        cl="cl",
        cs="cs",
        cp="cp",
        value="evec",
        vector="eval",
    ),
    restore_tensor=[
        "fa",
        "ga",
        "rgb",
        "md",
        "ad",
        "rd",
        "mode",
        "evec",
        "eval",
        "tensor",
    ],
    diffusion_kurtosis=[
        "fa",
        "ga",
        "rgb",
        "md",
        "ad",
        "rd",
        "mode",
        "evec",
        "eval",
        "mk",
        "ak",
        "rk",
        "dt_tensor",
        "dk_tensor",
    ],
)

KWARGS_MAPPING = dict(
    coreg_dwi_image="input_files",
    coreg_dwi_bval="bvalues_files",
    coreg_dwi_bvec="bvectors_files",
    coreg_dwi_brain_mask="mask_files",
)

TENSOR_FITTING_CMD = "dwi2tensor {input_files} -fslgrad {bvectors_files} {bvalues_files} - | tensor2metric - -force"


def build_tensor_fitting_cmd(kwargs, outputs):
    cmd = TENSOR_FITTING_CMD.format(**kwargs)
    for key, value in outputs.items():
        cmd += f" -{key} {value}"
    return cmd
