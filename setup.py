from setuptools import setup, find_packages

packages = ['core_tools', 'sample_specific', 'keysightSD1']
print('packages: {}'.format(packages))

setup(name="core_tools",
	version="1.1",
	packages = find_packages(),
	install_requires=[
          'pyqtgraph','si-prefix', 'matplotlib', 'psycopg2 '
      ],
	)
