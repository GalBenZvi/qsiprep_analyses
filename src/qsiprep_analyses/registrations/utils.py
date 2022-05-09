QUERIES = dict(
    mni2native={
        "main_key": "subject_specific",
        "sub_key": "mni_to_native_transform",
    },
    native2mni={
        "main_key": "subject_specific",
        "sub_key": "native_to_mni_transform",
    },
    anat_reference={
        "main_key": "subject_specific",
        "sub_key": "native_T1w",
    },
    probseg={
        "main_key": "subject_specific",
        "sub_key": "native_gm",
    },
    dwi_reference={"sub_key": "coreg_dwi_image"},
)

#: anatomical registration kets
ANAT_REG_KEYS = ["mni2native", "anat_reference", "probseg"]
#: Naming
DEFAULT_PARCELLATION_NAMING = dict(space="T1w", suffix="dseg", desc="")

#: Types of transformations
TRANSFORMS = ["mni2native", "native2mni"]

#: Default probability segmentations' threshold
PROBSEG_THRESHOLD = 0.01
