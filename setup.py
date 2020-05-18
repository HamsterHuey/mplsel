from setuptools import setup, find_packages


def readme():
    with open('README.md') as f:
        return f.read()


def get_version():
    return '0.0.1'

setup(
    name='mplsel',
    version=get_version(),
    packages=find_packages(),
    url='https://github.com/HamsterHuey/mplsel',
    license='MIT',
    author='Sudeep Mandal',
    author_email="sudeepmandal@gmail.com",
    description=('A utility class to enable easier selection, interaction, '
                 'modification and duplication of Line2D-based matplotlib plots'),
    long_description=readme(),
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'matplotlib>=3.0.3',
    ],
)

