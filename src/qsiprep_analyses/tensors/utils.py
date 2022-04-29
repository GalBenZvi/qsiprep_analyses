DWI_ENTITIES = dict(suffix="dwi", extension=".nii.gz", space="T1w")

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
    dwi="input_files",
    bval="bvalues_files",
    bvec="bvectors_files",
    # mask="mask_files",
    # out_metrics="save_metrics",
)

TENSOR_FITTING_CMD = "dwi2tensor {input_files} -fslgrad {bvectors_files} {bvalues_files} - | tensor2metric - -force"


def build_tensor_fitting_cmd(kwargs, outputs):
    cmd = TENSOR_FITTING_CMD.format(**kwargs)
    for key, value in outputs.items():
        cmd += f" -{key} {value}"
    return cmd
