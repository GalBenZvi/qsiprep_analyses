#: Errors
TENSOR_RECONSTRUCTION_NOT_IMPLEMENTED = "Estimation of {tensor_type}-derived metrics is not yet implemented."  # noqa: E501
INVALID_PARTICIPANT = "participant_label must describe an existing participant in QSIprep derivatives' directory ({base_dir}), but a value of {participant_label} was passed."  # noqa
#: Warnings
INVALID_OUTPUT = """Requested output {output} is not a valid ({tensor_type}) tensor-derived metric.
Available metrics are: {available_metrics}"""  # noqa: E501
