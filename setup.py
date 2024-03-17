from setuptools import find_packages, setup

setup(
    name="flasker",
    version="1.0.0",
    description="A blog site made with flask",
    author="E-code",
    author_email="ecode5814@gmail.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=["flask",],
)