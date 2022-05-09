import logging
from pathlib import Path
from typing import Union

from analyses_utils.entities.derivatives.qsiprep import QsiprepDerivatives
from analyses_utils.entities.participant import Participant

from qsiprep_analyses.utils.messages import (
    BASE_DIR_AND_PARTICIPANT_REQUIRED,
    MUTUALLY_EXCLUSIVE,
)

SIMPLE_LOGGING_FORMAT = "%(name)s - %(levelname)s\n\t%(message)s"


def get_console_handler() -> logging.StreamHandler:
    """
    Returns a console handler for logging.
    """
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(SIMPLE_LOGGING_FORMAT))
    return console_handler


def validate_instantiation(
    derivatives: QsiprepDerivatives = None,
    base_dir: Union[Path, str] = None,
    sessions_base: str = None,
    participant_label: str = None,
):
    """
    Validates the instansitation of *QsiprepAnalyses* class.
    *participant_label* and *derivatives* are mutually exclusive.
    """
    if participant_label and derivatives:
        raise ValueError(
            MUTUALLY_EXCLUSIVE.format(
                in1="participant_label", in2="derivatives"
            )
        )
    if not derivatives:
        if not (base_dir and participant_label):
            raise ValueError(BASE_DIR_AND_PARTICIPANT_REQUIRED)
        return QsiprepDerivatives(
            Participant(
                label=participant_label,
                base_dir=base_dir,
                sessions_base=sessions_base,
            )
        )
    return derivatives


def apply_bids_filters(original: dict, replacements: dict) -> dict:
    """
    Change an *original* bids-filters' query according to *replacements*

    Parameters
    ----------
    original : dict
        Original filters
    replacements : dict
        Replacement entities

    Returns
    -------
    dict
        Combined entities for bids query
    """
    combined_filters = original.copy()
    if isinstance(replacements, dict):
        for key, value in replacements.items():
            combined_filters[key] = value
    return combined_filters
