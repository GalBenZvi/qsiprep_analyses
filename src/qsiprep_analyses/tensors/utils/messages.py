#: Errors
TENSOR_RECONSTRUCTION_NOT_IMPLEMENTED = "Estimation of {tensor_type}-derived metrics is not yet implemented."  # noqa: E501
INVALID_PARTICIPANT = "participant_label must describe an existing participant in QSIprep derivatives' directory ({base_dir}), but a value of {participant_label} was passed."  # noqa
#: Warnings
INVALID_OUTPUT = """Requested output {output} is not a valid ({tensor_type}) tensor-derived metric.
Available metrics are: {available_metrics}"""  # noqa: E501
#: Messages
RUNNING_PARTICIPANT = "Executing "
RECONSTRUCTION_WORKFLOW = """Executing {tensor_type} reconstruction workflow with the following parameters:"""  # noqa: E501
OUTPUTS_EXIST = """Outputs for {tensor_type} reconstruction already exist for the following paramters:"""  # noqa: E501
