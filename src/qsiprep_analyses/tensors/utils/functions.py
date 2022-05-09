from pathlib import Path
from typing import Union

import dipy.denoise.noise_estimate as ne
from bids.layout import parse_file_entities
from bids.layout.writing import build_path
from dipy.io.image import load_nifti

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


def estimate_sigma(inputs: dict) -> float:
    """
    Estimate the noise standard deviation from the data and mask.

    Parameters
    ----------
    data : np.ndarray
        The data to be used for the estimation.

    Returns
    -------
    float
        The estimated noise standard deviation.
    """
    data, _ = load_nifti(inputs.get("input_files"))
    return ne.estimate_sigma(data)
