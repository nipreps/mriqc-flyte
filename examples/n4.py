import shutil
import subprocess
import tempfile
from pathlib import Path

import flyte
from flyte.io import File

env = flyte.TaskEnvironment(name="n4")


@env.task
async def n4(in_file: File) -> File:
    """Correct the intensity non-uniformity of ``in_file``."""
    in_path = await in_file.download()

    workdir = tempfile.mkdtemp(prefix="n4-")
    out_path = str(Path(workdir) / "corrected.nii.gz")

    # fmt: off
    cmd = [
        "N4BiasFieldCorrection",
        "-d", "3",
        "-i", in_path,
        "-o", out_path,
    ]

    # fmt: on
    subprocess.run(cmd, check=True)

    return await File.from_local(out_path)


@env.task
async def show_path(in_file: File) -> str:
    """Print the local path of ``in_file`` and the file's size, and return the path."""
    path = await in_file.download()
    print(path, Path(path).stat().st_size)
    return path


@env.task
async def main(in_file: File, delete_workdir: bool = False) -> str:
    """Run ``n4``, delete its folder if asked, then run ``show_path`` on its output."""
    corrected = await n4(in_file)
    if delete_workdir:
        shutil.rmtree(Path(corrected.path).parent)

    return await show_path(corrected)
