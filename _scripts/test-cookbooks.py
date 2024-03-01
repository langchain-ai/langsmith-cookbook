import argparse
import contextlib
import os
import glob
import re
import time

import nbformat
from nbconvert.preprocessors import ExecutePreprocessor
from langsmith import Client

filter_list = {
    "llm_run_etl.ipynb",
    "lilac.ipynb",
    "fine-tuning-on-chat-runs.ipynb",
    "vision-evals.ipynb",
    "contract-extraction.ipynb",
    "LangSmith_TS_Demo-Traceable.ipynb",
    "multimodal.ipynb",
    "tool-selection.ipynb",
}
API_KEY_REGEX = r'os\.environ\["LANGCHAIN_API_KEY"\] = [\"\']([^\"\']+)["\']'
HUB_API_KEY_REGEX = r'os\.environ\["LANGCHAIN_HUB_API_KEY"\] = [\"\']([^\"\']+)["\']'
ENDPOINT_REGEX = r'os\.environ\["LANGCHAIN_ENDPOINT"\] = [\"\']([^\"\']+)["\']'
HUB_API_URL_REGEX = r'os\.environ\["LANGCHAIN_HUB_API_URL"\] = [\"\']([^\"\']+)["\']'
PROJECT_ENV_REGEX = r'os\.environ\["LANGCHAIN_PROJECT"\] = [\"\']([^\"\']+)["\']'
PROJECT_NAME_REGEX = r"YOUR PROJECT NAME"
HUB_HANDLE_REGEX = r"YOUR HUB HANDLE"
OPENAI_API_KEY_REGEX = r'os\.environ\["OPENAI_API_KEY"\] = [\"\']([^\"\']+)["\']'


def _run_notebook(
    filename,
    api_key,
    endpoint,
    project,
    hub_api_key,
    hub_api_url,
    hub_handle,
    openai_api_key,
):
    """
    Execute a notebook via nbconvert and collect output. Also replace important env variables
    """
    with open(filename) as ff:
        nb_in = nbformat.read(ff, nbformat.NO_CONVERT)
    for cell in nb_in.cells:
        if cell.cell_type == "code":
            if re.search(API_KEY_REGEX, cell.source):
                cell.source = re.sub(
                    API_KEY_REGEX,
                    f"os.environ[\"LANGCHAIN_API_KEY\"] = '{api_key}'",
                    cell.source,
                )
            if re.search(ENDPOINT_REGEX, cell.source):
                cell.source = re.sub(
                    ENDPOINT_REGEX,
                    f'os.environ["LANGCHAIN_ENDPOINT"] = "{endpoint}"',
                    cell.source,
                )
            if re.search(PROJECT_ENV_REGEX, cell.source):
                cell.source = re.sub(
                    PROJECT_ENV_REGEX,
                    f"os.environ[\"LANGCHAIN_PROJECT\"] = '{project}'",
                    cell.source,
                )
            if re.search(PROJECT_NAME_REGEX, cell.source):
                cell.source = re.sub(PROJECT_NAME_REGEX, project, cell.source)
            if re.search(HUB_API_KEY_REGEX, cell.source):
                cell.source = re.sub(
                    HUB_API_KEY_REGEX,
                    f"os.environ[\"LANGCHAIN_HUB_API_KEY\"] = '{hub_api_key}'",
                    cell.source,
                )
            if re.search(HUB_API_URL_REGEX, cell.source):
                cell.source = re.sub(
                    HUB_API_URL_REGEX,
                    f"os.environ[\"LANGCHAIN_HUB_API_URL\"] = '{hub_api_url}'",
                    cell.source,
                )
            if re.search(HUB_HANDLE_REGEX, cell.source):
                cell.source = re.sub(HUB_HANDLE_REGEX, hub_handle, cell.source)
            if re.search(OPENAI_API_KEY_REGEX, cell.source):
                cell.source = re.sub(
                    OPENAI_API_KEY_REGEX,
                    f"os.environ[\"OPENAI_API_KEY\"] = '{openai_api_key}'",
                    cell.source,
                )

    ep = ExecutePreprocessor(timeout=1000, allow_errors=False)
    backoff = 1
    while backoff < 10:
        try:
            nb_out = ep.preprocess(nb_in)
            return nb_out
        except Exception as e:
            print(
                f"Failed to run notebook {filename} with error {e}. Retrying in {backoff} seconds"
            )
            time.sleep(backoff)
            backoff *= 2
            if backoff >= 10:
                raise


@contextlib.contextmanager
def set_env(**environ):
    """
    Temporarily set the process environment variables. This helps us avoid overwriting env variables that might
    already be set.
    """
    old_environ = dict(os.environ)
    os.environ.update(environ)
    try:
        yield
    finally:
        os.environ.clear()
        os.environ.update(old_environ)


parser = argparse.ArgumentParser()
parser.add_argument(
    "-e",
    "--endpoint",
    required=False,
    help="Langsmith host to connect to",
    default="https://api.smith.langchain.com",
)
parser.add_argument(
    "-he",
    "--hub-endpoint",
    required=False,
    help="Langsmith host to connect to",
    default="https://api.hub.langchain.com",
)
parser.add_argument(
    "-p",
    "--project",
    required=False,
    help="Project to use for your notebook",
    default="default",
)
parser.add_argument("-a", "--api-key", help="API key to use")
parser.add_argument("-ha", "--hub-api-key", help="Hub API key to use", default="")
parser.add_argument("-n", "--notebook", help="Notebook to run", default="*")
parser.add_argument("-hh", "--hub-handle", help="Hub handle", default="")
parser.add_argument(
    "-oai",
    "--openai-api-key",
    help="OpenAI API key",
    default=os.environ.get("OPENAI_API_KEY", ""),
)

new_env = {"LANGCHAIN_TRACING_V2": "true"}
args = parser.parse_args()
if not args.api_key:
    raise Exception("No API key provided")

client = Client(api_url=args.endpoint, api_key=args.api_key)
# Create project if not found
try:
    client.read_project(project_name=args.project)
except Exception as e:
    client.create_project(args.project)

with set_env(**new_env):
    for file in glob.glob(f"../**/{args.notebook}.ipynb", recursive=True):
        if file.split("/")[-1] in filter_list:
            print(f"Skipping {file}")
            continue
        print(f"Running notebook {file}")
        output = _run_notebook(
            file,
            args.api_key,
            args.endpoint,
            args.project,
            args.api_key,
            args.hub_endpoint,
            args.hub_handle,
            args.openai_api_key,
        )
