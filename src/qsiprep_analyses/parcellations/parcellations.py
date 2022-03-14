"""
Definition of the :class:`NativeParcellation` class.
"""
from pathlib import Path
from typing import Callable, Union

import numpy as np
import pandas as pd
from brain_parts.parcellation.parcellations import (
    Parcellation as parcellation_manager,
)
from tqdm import tqdm

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
        self,
        participant_label: str,
        session: Union[str, list],
        tensor_type: str,
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
        metrics = self.tensor_estimation.METRICS.get(tensor_type)
        return pd.MultiIndex.from_product(
            [[participant_label], sessions, metrics]
        )

    def build_output_name(
        self,
        parcellation_scheme: str,
        parcellation_type: str,
        tensor_type: str,
        parcellation_image: Union[Path, str],
        measure: Callable = np.nanmean,
    ) -> Path:
        """
        Reconstruct output "table"'s path

        Parameters
        ----------
        parcellation_scheme : str
            Parcellation scheme to parcellate by
        parcellation_type : str
            Either "Whole_brain" or "gm_cropped"
        tensor_type : str
            Tensor reconstruction method
        parcellation_image : Union[Path, str]
            Subject-specific parcellation image
        measure : Callable, optional
            Measure to parcellate by, by default np.nanmean

        Returns
        -------
        Path
            Path to output table.
        """
        measure = measure.__name__
        acquisition = self.tensor_estimation.TENSOR_TYPES.get(tensor_type).get(
            "acq"
        )
        entities = {
            "atlas": parcellation_scheme,
            "suffix": "dseg",
            "acquisition": acquisition,
            "extension": ".pickle",
            "measure": measure,
        }
        parts = parcellation_type.split("_")
        entities["desc"] = "".join([parts[0], parts[1].capitalize()])
        return self.data_grabber.build_path(parcellation_image, entities)

    def parcellate_single_tensor(
        self,
        parcellation_scheme: str,
        tensor_type: str,
        participant_label: str,
        parcellation_type: str = "whole_brain",
        session: Union[str, list] = None,
        measure: Callable = np.nanmean,
        force: bool = False,
    ) -> pd.DataFrame:
        """
        Parcellate tensor-derived metrics

        Parameters
        ----------
        parcellation_scheme : str
            Parcellation scheme to parcellate by
        tensor_type : str
            Tensor reconstruction method
        participant_label : str
            Specific participant's label
        parcellation_type : str, optional
            Either "gm_cropped" or "whole_brain", by default "gm_cropped"
        session : Union[str, list], optional
            Specific session's label, by default None
        measure : Callable, optional
            Measure for parcellation, by default np.nanmean
        force : bool, optional
            Whether to re-write existing files, by default False

        Returns
        -------
        pd.DataFrame
            A DataFrame with (participant_label,session,tensor_type,metrics)
            as index and (parcellation_scheme,label) as columns
        """
        rows = self.generate_rows(participant_label, session, tensor_type)
        tensors = self.tensor_estimation.run_single_subject(
            participant_label, session, tensor_type
        )
        parcellation_images = self.registration_manager.run_single_subject(
            parcellation_scheme,
            participant_label,
            participant_label,
            session,
            force=force,
        )
        data = pd.DataFrame(index=rows)
        for session in rows.levels[1]:
            parcellation = parcellation_images.get(session).get(
                parcellation_type
            )
            output_file = self.build_output_name(
                parcellation_scheme,
                parcellation_type,
                tensor_type,
                parcellation,
                measure,
            )
            if output_file.exists() and not force:
                return pd.read_pickle(output_file)
            for metric, metric_image in (
                tensors.get(session).get(tensor_type)[0].items()
            ):
                key = metric.split("_")[-1]

                tmp_data = self.parcellation_manager.parcellate_image(
                    parcellation_scheme,
                    parcellation,
                    metric_image,
                    key,
                    measure=measure,
                )
                data.loc[
                    (participant_label, session, key),
                    tmp_data.index,
                ] = tmp_data.loc[tmp_data.index]
            data.to_pickle(output_file)
        return data

    def parcellate_single_subject(
        self,
        parcellation_scheme: str,
        participant_label: str,
        parcellation_type: str = "whole_brain",
        session: Union[str, list] = None,
        measure: Callable = np.nanmean,
        force: bool = False,
    ) -> pd.DataFrame:
        """
        Perform all parcellation available for a single subject

        Parameters
        ----------
        parcellation_scheme : str
            Parcellation scheme to parcellate by
        participant_label : str
            A single participant's label
        parcellation_type : str, optional
            Either "whole_brain" or "gm_cropped", by default "whole_brain"
        session : Union[str, list], optional
            A specific session's label, by default None
        measure : Callable, optional
            Measure to parcellate by, by default np.nanmean
        force : bool, optional
            Whether to re-write existing files, by default False

        Returns
        -------
        pd.DataFrame
            All subject's availble parcellated data
        """
        data = pd.DataFrame()
        for tensor_type in self.tensor_estimation.TENSOR_TYPES:
            tensor_data = self.parcellate_single_tensor(
                parcellation_scheme,
                tensor_type,
                participant_label,
                parcellation_type,
                session,
                measure,
                force,
            )
            tensor_data = pd.concat([tensor_data], keys=[tensor_type])
            data = pd.concat([data, tensor_data])
        return data

    def parcellate_dataset(
        self,
        parcellation_scheme: str,
        parcellation_type: str = "whole_brain",
        measure: Callable = np.nanmean,
        force: bool = False,
    ):
        data = pd.DataFrame()
        for participant_label in tqdm(self.subjects):
            data = pd.concat(
                [
                    data,
                    self.parcellate_single_subject(
                        parcellation_scheme,
                        participant_label,
                        parcellation_type,
                        measure=measure,
                        force=force,
                    ),
                ]
            )
        return data
