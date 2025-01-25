
from pathlib import Path
from uuid import uuid4

import pikepdf
import fitz

from tokenpdf.utils.general import rename
from tokenpdf.utils.verbose import vprint, vtqdm
class FilePostProcess:
    """ """
    @staticmethod
    def process(path, config, loader):
        """

        Args:
          path: 
          config: 
          loader: 

        Returns:

        """
        path = Path(path)
        verbose = config.get("verbose", False)
        print = vprint(verbose)
        if config.get("compress") and path.suffix == ".pdf":
            print("Compressing PDF...")
            FilePostProcess.compress_pdf(path, verbose)


    @staticmethod
    def compress_pdf(path, verbose=False):
        """

        Args:
          path: 
          verbose:  (Default value = False)

        Returns:

        """
        temp_name = path.with_suffix(f".{uuid4().hex[:8]}.pdf")
        tqdm = vtqdm(verbose)
        
        
        file_size_pre = path.stat().st_size
        with rename(path, temp_name, delete_on_cancel=True) as r:
            FilePostProcess.compress_pdf_pikepdf(temp_name, path, tqdm)
            r.cancel()
        file_size_post = path.stat().st_size
        print(f"Compressed PDF from {file_size_pre} to {file_size_post} bytes")
        print(f"Total compression: {100 * (1 - file_size_post / file_size_pre):.2f}%")
                         
    @staticmethod
    def compress_pdf_pikepdf(input_path, output_path, tqdm):
        """

        Args:
          input_path: 
          output_path: 
          tqdm: 

        Returns:

        """
        progress = tqdm(desc="Compressing PDF", total=100)
        with pikepdf.open(input_path) as pdf:
            pdf.save(output_path,
                        compress_streams=True,
                        object_stream_mode=pikepdf.ObjectStreamMode.generate,
                        progress=progress.update)
        progress.close()

            
            