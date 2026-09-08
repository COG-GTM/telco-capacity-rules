from setuptools import find_packages, setup


setup(
    name="telco-capacity-rules",
    version="0.2.0",
    description="Shared capacity rules for telco estates",
    packages=find_packages(),
    package_data={
        "telco_capacity": ["vectors.json"],
        "telco_rules": ["billing_vectors.json"],
    },
    install_requires=[],
)
