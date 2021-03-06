import logging
from pathlib import PurePath, PurePosixPath


logger = logging.getLogger("datalad.metadata.model")


class MetadataPath(PurePosixPath):
    def __new__(cls, *args):
        original_path = PurePath(*args)
        if not original_path.is_absolute():
            created_path = super().__new__(
                cls,
                "/".join(original_path.parts))
        else:
            created_path = super().__new__(
                cls,
                "/".join(original_path.parts[1:]))
            logger.warning(
                f"Denied creation of absolute metadata path: {original_path}, "
                f"created {created_path} instead. This is considered an error "
                f"in the calling code.")

        return created_path

    def __str__(self):
        path_str = PurePosixPath.__str__(self)
        return (
            ""
            if path_str == "."
            else path_str)
