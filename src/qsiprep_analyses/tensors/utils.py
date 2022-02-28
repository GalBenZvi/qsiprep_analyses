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
