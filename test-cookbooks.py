import argparse
import contextlib
import os
import glob

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor


def run_notebook(filename):
    with open(filename) as ff:
        nb_in = nbformat.read(ff, nbformat.NO_CONVERT)

    ep = ExecutePreprocessor(timeout=600)

    nb_out = ep.preprocess(nb_in)
    return nb_out


@contextlib.contextmanager
def set_env(**environ):
    """
    Temporarily set the process environment variables.
    """
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


parser = argparse.ArgumentParser()
parser.add_argument("-e", "--endpoint", required=False, help="Langsmith host to connect to",
                    default="https://api.smith.langchain.com")
parser.add_argument("-p", "--project", required=False, help="Project to upload to", default="default")
parser.add_argument("-a", "--api_key", help="API key to use")

new_env = {"LANGCHAIN_TRACING_V2": "true"}
args = parser.parse_args()
if not args.api_key:
    raise Exception("No API key provided")
new_env["LANGCHAIN_API_KEY"] = args.api_key
new_env["LANGCHAIN_ENDPOINT"] = args.endpoint
new_env["LANGCHAIN_PROJECT"] = args.project

with set_env(**new_env):
    for file in glob.glob("**/*.ipynb", recursive=True):
        print(f"Running notebook {file}")
        run_notebook(file)
