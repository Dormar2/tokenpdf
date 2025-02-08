
from pathlib import Path
from uuid import uuid4

import pikepdf
import PyPDF2


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
        if path.suffix == ".pdf":
            cleanup = config.get("cleanup", 1)
            if cleanup:
                print("Cleaning up PDF...")
                FilePostProcess.cleanup_pdf(path, verbose, level=cleanup)
            if config.get("compress") and path.suffix == ".pdf":
                print("Compressing PDF...")
                FilePostProcess.compress_pdf(path, verbose)



    @staticmethod
    def safe_op(func, path, verbose=False, **kwargs):
        """ Calls a path->path function as if its inplace
        by properly renaming the file temporarily, and
        If the function fails, the original file is not lost.
        
        Args:
            func: A function with the signature func(input:Path, output:Path, tqdm:Callable)
        """
        path = Path(path)
        tqdm = vtqdm(verbose)
        temp_name = path.with_suffix(f".{uuid4().hex[:8]}{path.suffix}")
        with rename(path, temp_name, delete_on_cancel=True) as r:
            func(temp_name, path, tqdm, **kwargs)
            r.cancel()


    @staticmethod
    def cleanup_pdf(path, verbose=False, level=1):
        FilePostProcess.safe_op(FilePostProcess._cleanup_pdf_pypdf2, path, verbose, level=level)


    @staticmethod
    def _cleanup_pdf_pypdf2(input_path, output_path, tqdm, level=1):
        #level 3: Require XObject contents (images, forms, etc)
        #level 2: Require XObject node
        #level 1: Require Resources node
        pdf = PyPDF2.PdfReader(input_path)
        pdf_writer = PyPDF2.PdfWriter()
        for page in pdf.pages:
            has_content = False
            if page.extract_text().strip():
                has_content = True
            
            has_resources = '/Resources' in page
            has_xobject = has_resources and '/XObject' in page['/Resources']
            if level < 2:
                has_content = has_content or has_resources
            elif level < 3:
                has_content = has_content or has_xobject
            elif has_xobject:
                for obj in page['/Resources']['/XObject'].values():
                    if not hasattr(obj, '__getitem__'):
                        continue
                    if '/Subtype' not in obj:
                        continue
                    if obj['/Subtype'] in ['/Image', '/Form', '/Group']:
                        has_content = True
                        break
            if has_content:
                pdf_writer.add_page(page)
        pdf_writer.write(output_path)
        pdf_writer.close()
        

    @staticmethod
    def compress_pdf(path, verbose=False):
        """

        Args:
          path: 
          verbose:  (Default value = False)

        Returns:

        """
        
        
        
        file_size_pre = path.stat().st_size
        FilePostProcess.safe_op(FilePostProcess.compress_pdf_pypdf2, path, verbose)
        FilePostProcess.safe_op(FilePostProcess.compress_pdf_pikepdf, path, verbose)
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

    @staticmethod
    def compress_pdf_pypdf2(input_path, output_path, tqdm):
        pdf = PyPDF2.PdfReader(input_path)
        pdf_writer = PyPDF2.PdfWriter()
        for page in pdf.pages:
            page.compress_content_streams()
            pdf_writer.add_page(page)
        
        pdf_writer.write(output_path)
        pdf_writer.close()
        return output_path
            
            