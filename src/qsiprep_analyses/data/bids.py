from pathlib import Path
from typing import Union

from bids.layout import parse_file_entities
from bids.layout.writing import build_path

BIDS_CONFIGURATION_FILE = (
    Path(__file__).parent / "derivatives.json"
).absolute()
# flake8: noqa: E501
DEFAULT_PATTERNS = [
    "sub-{subject}[/ses-{session}]/{datatype<dwi>|dwi}/sub-{subject}[_ses-{session}][_acq-{acquisition}][_dir-{direction}][_space-{space}][_res-{resolution}][_desc-{desc}][_part-{part}]_{suffix<dwi|dwiref|epiref|mask>}{extension<.bval|.bvec|.json|.nii.gz|.nii>|.nii.gz}",
    "sub-{subject}[/ses-{session}]/{datatype<anat>|anat}/sub-{subject}[_ses-{session}][_acq-{acquisition}][_ce-{ceagent}][_rec-{reconstruction}][_space-{space}][_res-{resolution}][_part-{part}]_{suffix<T1w|T2w|T1rho|T1map|T2map|T2star|FLAIR|FLASH|PDmap|PD|PDT2|inplaneT[12]|angio>}{extension<.nii|.nii.gz|.json>|.nii.gz}",
    "sub-{subject}[/ses-{session}]/{datatype<anat|dwi>|anat}/sub-{subject}[_ses-{session}][_acq-{acquisition}][_dir-{direction}][_ce-{ceagent}][_rec-{reconstruction}][_space-{space}][_res-{res}][_res-{resolution}][_desc-{desc}][_label-{label}][_meas-{measure}][_atlas-{atlas}]_{suffix<dseg>}{extension<.csv|.tsv|.pickle|.nii|.nii.gz|.json>|.nii.gz}",
]


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
