#                      M""""""""`M            dP
#                      Mmmmmm   .M            88
#                      MMMMP  .MMM  dP    dP  88  .dP   .d8888b.
#                      MMP  .MMMMM  88    88  88888"    88'  `88
#                      M' .MMMMMMM  88.  .88  88  `8b.  88.  .88
#                      M         M  `88888P'  dP   `YP  `88888P'
#                      MMMMMMMMMMM    -*-  Created by Zuko  -*-
#
#                      * * * * * * * * * * * * * * * * * * * * *
#                      * -    - -   F.R.E.E.M.I.N.D   - -    - *
#                      * -  Copyright © 2026 (Z) Programing  - *
#                      *    -  -  All Rights Reserved  -  -    *
#                      * * * * * * * * * * * * * * * * * * * * *



#
#
from setuptools import setup, find_packages

with open('README.md', 'r', encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='pyside6-datatable-widget',
    version='1.1.0.6',
    author='Zuko',
    author_email='tansautn@gmail.com',
    description='A PySide6 DataTable widget with jQuery DataTable-like functionality',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/ultra-bugs/pyside6-datatable-widget',
    project_urls={'Bug Tracker': 'https://github.com/ultra-bugs/pyside6-datatable-widget/issues'},
    license='GPLv3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: User Interfaces',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
    ],
    package_dir={'': '.'},
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=['PySide6>=6.1.0', 'better-exceptions', 'loguru'],
)
