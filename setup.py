from setuptools import setup, find_packages

with open("requirements.txt") as f:
	install_requires = f.read().strip().split("\n")

setup(
	name="clearing_forwarding",
	version="0.0.1",
	description="Clearing & Forwarding Management System for ERPNext 16",
	author="Wycliffs",
	author_email="",
	packages=find_packages(),
	zip_safe=False,
	include_package_data=True,
	install_requires=install_requires,
)
