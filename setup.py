from distutils.core import setup

setup(
    name="rta-transient-receiver",
    author="Antonio Addis",
    version="1.0.0",
    packages=['comet/plugins', "comet/plugins/test"],
    include_package_data=True,
    package_data = {'mypkg': [
                         'comet/plugins/*.yml']},
    license='GPL-3.0'
)
