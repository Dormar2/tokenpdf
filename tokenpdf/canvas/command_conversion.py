import subprocess
import logging
import os
from typing import List, Tuple
from pathlib import Path
from tempfile import mkstemp
from .canvas import Canvas, ConvertCanvasWrapper
from tokenpdf.utils.os import find_executable, unsafe_temp_filepath
from tokenpdf.utils.general import set_attr

logger = logging.getLogger(__name__)


class ConvertByCommandCanvas(ConvertCanvasWrapper):
    def __init__(self, 
                 subcanvas, config, 
                 file_path=None, 
                 many_to_one=False):
        super().__init__(subcanvas, config, file_path)
        self.many_to_one = many_to_one
        self.return_result = False
        self._output_files = []
        self._input_files = []
    
    def convert(self, result, verbose, return_result=False):
        if not return_result and isinstance(result, list|tuple) and len(result) > 1 and not self.many_to_one:
            raise ValueError("Cannot convert multiple results without returning them")
        try:
            with set_attr(self, return_result=return_result, _output_files=[], _input_files=[]):
                if self.many_to_one or not isinstance(result, list|tuple):
                    cmd = self._make_command(result, verbose)
                    self._run_command(cmd, verbose)
                else:
                    for res in result:
                        cmd = self._make_command(res, verbose)
                        self._run_command(cmd, verbose)
                if return_result:
                    outputs = []
                    for output_path in self._output_files:
                        outputs.append(Path(output_path).read_text())
                    return outputs
        finally:
            self.cleanup()
        
            
    def cleanup(self):
        for file in (self._input_files + self._output_files):
            try:
                file.unlink()
            except Exception:
                logger.warning(f"Could not delete {file}")
        self._input_files = []
        self._output_files = []
        self.subcanvas.cleanup()
        super().cleanup()

    def _get_output(self, suffix=None) -> Path:
        """ Get a new output path """
        if not self.return_result:
            if self._output_files:
                raise ValueError("Cannot get multiple output files without returning them")
            self._output_files.append(self.file_path)
            return self.file_path
        output_path = unsafe_temp_filepath(suffix=suffix)
        self._output_files.append(output_path)
        return output_path
    
    def _get_input(self, suffix=None) -> Path:
        input_path = unsafe_temp_filepath(suffix=suffix)
        self._input_files.append(input_path)
        return input_path
    
    def _to_input(self, result, suffix=None):
        if isinstance(result, str):
            temp = self._get_input(suffix=suffix)
            temp.write_text(result)
            return temp
        elif isinstance(result, bytes):
            temp = self._get_input(suffix=suffix)
            temp.write_bytes(result)
            return temp
        elif isinstance(result, List|Tuple):
            return [self._to_input(res, suffix=suffix) for res in result]
        

    def _run_command(self, cmd, verbose):
        if not Path(cmd[0]).exists():
            raise FileNotFoundError(f"Executable not found: {cmd[0]}")
        if verbose:
            subprocess.run(cmd, shell=True)
        else:
            subprocess.run(cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
    def _make_command(self, result, verbose):
        raise NotImplementedError("Subclasses must implement this method")

    def _find_executable(self, repo, name=None):
        executable_overrides = self.config.get("executables", {})
        bin_root_override = self.config.get("bin_dir", None)
        return find_executable(repo, name, executable_overrides=executable_overrides, bin_root_override=bin_root_override)