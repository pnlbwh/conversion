from setuptools import setup, find_packages

requirements= open('requirements.txt').read().split()
print(requirements)

setup(name='conversion',
    version='1.0',
    description='Python utility scripts for MRI processing',
    author='Tashrif Billah',
    author_email='tb571@bwh.harvard.edu, tashrifbillah@gmail.com',
    url='https://github.com/pnlbwh/conversion',
    license='MIT License',
    install_requires=requirements,
    packages=find_packages(exclude=('*tests*',)),
    package_data={'tests':'tests/*', 'data':'data/*'},
    project_urls={'Tracker':'https://github.com/pnlbwh/conversion/issues',
                    'Documentation':'https://github.com/pnlbwh/conversion/README.md'},
    )
