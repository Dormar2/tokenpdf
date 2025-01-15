import os


def main():
    """ """
    # Make stubs using pyment
    input = None
    output = "google"

    input_args = f" --input {input}" if input else ""
    output_args = f" --output {output}"
    cmd = f"pyment{input_args}{output_args} -d -w ."
    os.system(cmd)
    

if __name__ == "__main__":
    main()
    



