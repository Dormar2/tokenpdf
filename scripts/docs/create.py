import os
import logging

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def main():
    """Generate docstring stubs using Pyment with Google-style formatting."""
    input_path = None  # Directory or file to process (None means current directory)
    output_style = "google"  # Docstring style to use

    # Construct the Pyment command
    input_args = f" --input {input_path}" if input_path else ""
    output_args = f" --output {output_style}"
    cmd = f"pyment{input_args}{output_args} -d -w ."

    logger.info(f"Running Pyment command: {cmd}")
    os.system(cmd)


if __name__ == "__main__":
    main()