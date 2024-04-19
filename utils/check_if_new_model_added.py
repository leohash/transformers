# Copyright 2024 The HuggingFace Team. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
This script is used to get the directory of the modeling file that is added in a pull request (i.e. a new model PR).

Usage:

```bash
python utils/check_if_new_model_added.py
```
"""

from pathlib import Path
import re
from typing import List

from git import Repo


PATH_TO_REPO = Path(__file__).parent.parent.resolve()


def get_new_files(base_commit: str, commits: List[str]) -> List[str]:
    """
    Get the diff between a base commit and one or several commits.

    Args:
        repo (`git.Repo`):
            A git repository (for instance the Transformers repo).
        base_commit (`str`):
            The commit reference of where to compare for the diff. This is the current commit, not the branching point!
        commits (`List[str]`):
            The list of commits with which to compare the repo at `base_commit` (so the branching point).

    Returns:
        `List[str]`: The list of Python files with a diff (files added, renamed or deleted are always returned, files
        modified are returned if the diff in the file is not only in docstrings or comments, see
        `diff_is_docstring_only`).
    """
    code_diff = []
    for commit in commits:
        for diff_obj in commit.diff(base_commit):
            # We always add new python files
            if diff_obj.change_type == "A" and diff_obj.b_path.endswith(".py"):
                code_diff.append(diff_obj.b_path)

    return code_diff


def get_new_python_files() -> List[str]:
    """
    Return a list of python files that have been added between:

    - the current head and the main branch if `diff_with_last_commit=False` (default)
    - the current head and its parent commit otherwise.

    Returns:
        `List[str]`: The list of python files added.
    """
    repo = Repo(PATH_TO_REPO)

    try:
        main = repo.refs.main
    except:
        main = repo.remotes.origin.refs.main

    print(f"main is at {main.commit}")
    print(f"Current head is at {repo.head.commit}")

    branching_commits = repo.merge_base(main, repo.head)
    for commit in branching_commits:
        print(f"Branching commit: {commit}")
    return get_new_files(repo.head.commit, branching_commits)


if __name__ == "__main__":
    new_files = get_new_python_files()
    reg = re.compile(r"src/transformers/(models/.*)/modeling_.*\.py")

    new_model = ""
    for x in new_files:
        find_new_model = reg.findall(x)
        if len(find_new_model) > 0:
            new_model = find_new_model[0]
        # It's unlikely we have 2 new modeling files in a pull request.
        break
    new_model = "models/bert"
    print(new_model)
