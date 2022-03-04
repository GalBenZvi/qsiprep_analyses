DWI_ENTITIES = dict(suffix="dwi", extension=".nii.gz")

TENSOR_DERIVED_ENTITIES = dict(suffix="dwiref", resolution="dwi")

TENSOR_DERIVED_METRICS = dict(
    diffusion_tensor=[
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
    dwi="input_files",
    bval="bvalues_files",
    bvec="bvectors_files",
    mask="mask_files",
    out_metrics="save_metrics",
)
