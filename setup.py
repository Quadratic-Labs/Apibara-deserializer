from setuptools import find_packages, setup

# with open("README.rst") as f:
#     readme = f.read()

# with open("LICENSE") as f:
#     license = f.read()

setup(
    name="apibara-deserializer",
    version="0.0.1",
    description="Deserialize apibara events to Python types",
    # long_description=readme,
    # license=license,
    author="Quadratic Labs",
    author_email="web3@quadratic-labs.com",
    url="https://quadratic-labs.com",
    packages=find_packages(exclude=("tests", "docs")),
    install_requires=["apibara==0.5.16"],
)
