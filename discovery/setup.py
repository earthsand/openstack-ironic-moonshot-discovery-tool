from setuptools import setup, find_packages

setup(
    name='discovery-driver',
    version='1.0',

    description='Discovery driver',

    author='Sandhya Ganapathy',
    author_email='sandhya.ganapathy@hp.com',

    platforms=['Any'],

    scripts=[],

    provides=['ironic.tools.discovery',
              ],

    packages=find_packages(),
    include_package_data=True,

    entry_points={
        'ironic.tools.discovery': [
'moonshot=ironic.tools.discovery.moonshot_discovery_driver:MoonshotDiscovery',
        ],
    },

    zip_safe=False,
)
