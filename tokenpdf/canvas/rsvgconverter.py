

from .command_conversion import ConvertByCommandCanvas



class RsvgConvert(ConvertByCommandCanvas):
    def __init__(self, subcanvas, config, file_path=None, many_to_one=False):
        super().__init__(subcanvas, config, file_path, many_to_one=many_to_one)
        

    def _make_command(self, result, verbose):
        inputs = self._to_input(result, suffix=".svg")
        
        if not isinstance(inputs, tuple|list):
            inputs = [inputs]
        inputs = [str(i) for i in inputs]
        
        args = [str(self._find_executable("console-rsvg-convert", "rsvg-convert"))]
        args.extend(inputs)
        args.extend(["-f", "pdf",
                    "-o", str(self._get_output())])
        if verbose:
            print(f"Converting svg to pdf with resvg: {' '.join(args)}")
        return args
        