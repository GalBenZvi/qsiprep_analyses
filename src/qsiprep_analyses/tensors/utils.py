DWI_ENTITIES = dict(suffix="dwi", extension=".nii.gz")

TENSOR_DERIVED_ENTITIES = dict(suffix="dwiref", resolution="dwi")

TENSOR_DERIVED_METRICS = dict(
    dt=["fa", "ga", "rgb", "md", "ad", "rd", "mode", "evec", "eval"],
    dk=[
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
    ],
)

KWARGS_MAPPING = dict(
    dwi="input_files",
    bval="bvalues_files",
    bvec="bvectors_files",
    mask="mask_files",
    out_metrics="save_metrics",
)

KWARGS = "{outputs} {dwi} {bval} {bvec} {mask}"
DIPY_FIT_DTI_CMD = "dipy_fit_dti"
DIPY_FIT_DKI_CMD = "dipy_fit_dki"
RECONSTRUCTION_COMMANDS = dict(
    dt=DIPY_FIT_DTI_CMD, dk=DIPY_FIT_DKI_CMD, args=KWARGS
)
