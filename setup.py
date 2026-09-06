"""Setup configuration for sustainable_supply_chain."""
from setuptools import setup, find_packages

setup(
    name="sustainable_supply_chain",
    version="1.0.0",
    description="Sustainable Supply Chain Agent with Climate-Aware Logistics, Circularity, What-If Simulator & AI Assistant",
    author="Apex Global Supply Chain AI Team",
    packages=find_packages(),
    entry_points={
        "console_scripts": [
            "supply-chain-agent=sustainable_supply_chain.cli:main",
        ],
    },
    python_requires=">=3.8",
)
