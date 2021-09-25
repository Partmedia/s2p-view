from setuptools import setup

setup(name='s2p-view',
    version='0.1.2',
    description='S-Parameter Viewer',
    author='Kevin Zheng',
    author_email='kevinz5000@gmail.com',
    url='https://github.com/Partmedia/s2p-view',
    packages = ['s2p_view'],
    entry_points = {
        'console_scripts': ['s2p-view = s2p_view.main:main'],
    },
    install_requires=[
        'PyQt5-sip',
        'matplotlib',
        'scikit-rf==0.17.0',
    ],
    zip_safe = True,
    license = 'GPLv3',
)
