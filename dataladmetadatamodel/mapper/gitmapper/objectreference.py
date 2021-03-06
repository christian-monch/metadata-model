import enum
from pathlib import Path
from typing import Dict, List, Tuple

from .utils import lock_backend, unlock_backend
from .gitbackend.subprocess import git_ls_tree, git_update_ref, git_save_tree


class GitReference(enum.Enum):
    TREE_VERSION_LIST = "refs/datalad/dataset-tree-version-list"
    UUID_SET = "refs/datalad/dataset-uuid-set"
    DATASET_TREE = "refs/datalad/object-references/dataset-tree"
    METADATA = "refs/datalad/object-references/metadata"
    FILE_TREE = "refs/datalad/object-references/file-tree"


CACHED_OBJECT_REFERENCES: Dict[str, List[Tuple[str, str, str, str]]] = dict()


def add_object_reference(git_reference: GitReference,
                         flag: str,
                         object_type: str,
                         object_hash: str):

    if git_reference.value not in CACHED_OBJECT_REFERENCES:
        CACHED_OBJECT_REFERENCES[git_reference.value] = []

    CACHED_OBJECT_REFERENCES[git_reference.value].append((
        flag,
        object_type,
        object_hash,
        "object_reference:" + object_hash
    ))


def flush_object_references(realm: Path):
    global CACHED_OBJECT_REFERENCES

    for git_reference, cached_tree_entries in CACHED_OBJECT_REFERENCES.items():
        lock_backend(realm)
        try:
            existing_tree_entries = [
                tuple(line.split())
                for line in git_ls_tree(str(realm), git_reference)
            ]
        except RuntimeError:
            existing_tree_entries = []

        existing_tree_entries.extend(cached_tree_entries)
        tree_hash = git_save_tree(str(realm), existing_tree_entries)
        git_update_ref(str(realm), git_reference, tree_hash)
        unlock_backend(realm)

    CACHED_OBJECT_REFERENCES = dict()


def add_tree_reference(git_reference: GitReference, object_hash: str):
    add_object_reference(git_reference, "040000", "tree", object_hash)


def add_blob_reference(git_reference: GitReference, object_hash: str):
    add_object_reference(git_reference, "100644", "blob", object_hash)


def remove_object_reference(*args, **kwargs):
    # TODO: implement this function
    raise NotImplementedError
