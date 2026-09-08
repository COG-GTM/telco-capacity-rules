from setuptools import find_packages, setup


setup(
    name="telco-capacity-rules",
    version="0.1.0",
    description="Shared capacity rules for telco estates",
    packages=find_packages(),
    package_data={"telco_capacity": ["vectors.json"]},
    install_requires=[],
)
