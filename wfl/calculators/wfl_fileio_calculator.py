from pathlib import Path
import shutil
import tempfile
import warnings

from .utils import clean_rundir as utils_clean_rundir

class WFLFileIOCalculator():
    """Mixin class implementing some methods that should be available to every
    WFL calculator that does I/O via files, i.e. DFT calculators
    
    As a python mixin class, must be inherited from by the wrapping wfl calculator class _before_ the ASE calculator, i.e.
    
    .. code-block:: python
    
        from ase.calculators.dftcode import DftCodeCalculator as ASE_DftCodeCalculator
        class DftCodeCalculator(WFLFileIOCalculator, ASE_DftCodeCalculator):
            .
            .
            .


    Parameters
    ----------
    keep_files: bool / None / "default" / list(str), default "default"
        what kind of files to keep from the run
            True, "*" : everything kept
            None, False : nothing kept
            "default"   : default list, varies by calculator, usually only ones needed for NOMAD uploads
            list(str)   : list of file globs to save
    rundir_prefix: str / Path
        Run directory name prefix
    workdir: str / Path, default . at calculate time
        Path in which rundir (rundir_prefix + temp suffix) will be created.
    scratchdir: str / Path, default None
        temporary directory to execute calculations in and delete or copy back results (set by
        "keep_files") if needed.  For example, directory on a local disk with fast file I/O.
    kwargs: dict
        remaining superclass constructor kwargs
    """

    def __init__(self, /, keep_files, rundir_prefix, workdir=None, scratchdir=None, **kwargs):
        if "directory" in kwargs:
            raise ValueError("Cannot pass directory argument")

        super().__init__(**kwargs)

        self._wfl_keep_files = keep_files

        self._wfl_rundir_prefix = Path(rundir_prefix)
        if self._wfl_rundir_prefix.is_absolute():
            if self._wfl_workdir is not None:
                raise ValueError(f"Can not specify workdir {workdir} if rundir_prefix {rundir_prefix} is an absolute path")
        self._wfl_workdir = Path(workdir) if workdir is not None else Path(".")
        self._wfl_scratchdir = Path(scratchdir) if scratchdir is not None else None


    def setup_rundir(self):
        # set rundir to where we want final results to live
        rundir_path = self._wfl_workdir / self._wfl_rundir_prefix.parent
        rundir_path.mkdir(parents=True, exist_ok=True)
        self._cur_rundir = Path(tempfile.mkdtemp(dir=rundir_path, prefix=self._wfl_rundir_prefix.name))

        # set self.directory to where we want the calculation to actually run
        if self._wfl_scratchdir is not None:
            dir_name = str(self._cur_rundir.resolve()).replace("/", "", 1).replace("/", "_")
            directory = self._wfl_scratchdir / dir_name
            directory.mkdir(parents=True, exist_ok=True)
            self.directory = directory
        else:
            self.directory = self._cur_rundir


    def clean_rundir(self, _default_keep_files, calculation_succeeded):
        utils_clean_rundir(self.directory, self._wfl_keep_files, _default_keep_files, calculation_succeeded)
        if self._wfl_scratchdir is not None:
            for f in Path(self.directory).glob("*"):
                shutil.move(f, self._cur_rundir)
            if list(Path(self.directory).iterdir()) == []:
                warnings.warn(f"scratchdir {self.directory} is not empty, not deleting.")
            else:
                Path(self.directory).rmdir()
                self.directory = '.' 
