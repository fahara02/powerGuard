from setuptools import setup, find_packages
from setuptools.command.install import install
import subprocess

class CustomInstallCommand(install):
    def run(self):
        # Run the protoc command to generate the Python files from the .proto files
        subprocess.check_call(['protoc', '--python_out=src/proto', 'src/proto/*.proto'])
        install.run(self)

setup(
    name="powerguard",
    version="0.1",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    cmdclass={
        'install': CustomInstallCommand,
    },
)
