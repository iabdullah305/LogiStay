from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

# get version from __version__ variable in logistay/__init__.py
from logistay import __version__ as version

setup(
	name="logistay",
	version=version,
	description="Fleet Management",
	author="AFMCOltd",
	author_email="afm@afmcoltd.com",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires
)