from .pipeline.workflow import WorkflowManager
from .utils.config import get_data_folder
from argparse import ArgumentParser

def main():
    parser = ArgumentParser(description="Generate PDFs of RPG tokens")
    # Configuration files (0 or more)
    parser.add_argument("config", nargs="*", help="Configuration file(s) to load. If none are provided, example.toml will be used. "
                        "Formats supported: JSON, TOML, YAML, INI (ConfigParser)")
    # Output file
    parser.add_argument("-o", "--output", default=None, help="The output file for the PDF. If not provided, output.pdf will be used.")
    # Verbose
    parser.add_argument("-v", "--verbose", action="store_true", 
                        help="Print information during execution. Default: Refers to the configuration file.")
    parser.add_argument("-s", "--silent", action="store_true", 
                        help="Silence most output. Default: Refers to the configuration file.")
    

    args = parser.parse_args()
    config_files = args.config
    if not config_files:
        config_files = [get_data_folder() / "example.toml"]
    output_file = args.output
    verbose = None if (not args.verbose and not args.silent) else (args.verbose and not args.silent)
    workflow = WorkflowManager(*config_files, output_file=output_file, verbose=verbose)
    workflow.run()

if __name__ == "__main__":
    main()
    