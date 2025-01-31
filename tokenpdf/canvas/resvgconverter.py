

from tokenpdf.canvas.canvas import ConvertCanvasWrapper
from .command_conversion import ConvertByCommandCanvas



class ResvgConvert(ConvertByCommandCanvas):
    def __init__(self, subcanvas, config, file_path=None, many_to_one=False):
        super().__init__(subcanvas, config, file_path, many_to_one=many_to_one)
        

    def _make_command(self, result, verbose):
        if self.many_to_one:
            raise NotImplementedError("Many to one conversion not yet supported by resvg")
        inputs = self._to_input(result, suffix=".svg")
        
        if not isinstance(inputs, tuple|list):
            inputs = [inputs]
        
        args = [self._find_executable("resvg")]
        args.extend(inputs)
        args.extend(["-o", {self._get_output()}])
        if verbose:
            print(f"Converting svg to pdf with resvg: {' '.join(args)}")
        return args
    
    @ConvertCanvasWrapper.converted_name.getter
    def converted_name(self):
        return "pdf"