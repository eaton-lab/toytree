#!/usr/bin/env python

"""Call an R script to test a related function in R.
"""

import subprocess
import tempfile
from textwrap import dedent


def run_r_script(r_code: str) -> str:
    """Write an R script to temp, execute it, and return stdout.
    
    Parameters
    ----------    
    r_code: str
        The R code to execute.
    """
    with tempfile.NamedTemporaryFile(mode="w", suffix=".R", delete=False) as tmpfile:
        tmpfile.write(r_code)
        tmpfile_path = tmpfile.name
        tmpfile.flush()

        try:
            cmd = ["Rscript", tmpfile_path]
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return result.stdout
        except subprocess.CalledProcessError as e:
            return f"Error: {e.stderr}"


if __name__ == "__main__":

    # Example usage
    r_script = dedent("""
    x <- rnorm(10)
    print(mean(x))
    """)

    output = run_r_script(r_script)
    print("R Output:", output)
