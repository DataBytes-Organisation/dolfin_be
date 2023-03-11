import sys
import pytest
import os

#sys.path.append("./src")
sys.path.append("./tests")

@pytest.fixture(autouse=True, scope="module")
def environment_vars():
    os.environ["BUCKET_NAME"] = "dolfin_bucket"