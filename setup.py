import setuptools
setuptools.setup(
    name="Rheometer Control",
    version="1.0.0",
    author="Shreyansh Chauhan",
    author_email='cshraiyansh@gmail.com',
    description="Will control the DAQ and Record the movement via a camera. Will control the magnetic field so that we can test the movement of our substarte. Its just the 1st part of Project for data acqusition",
    # long_description="A longer description of your project",
    # url="https://github.com/your_username/your_project",
    license="IISc",
    keywords="CeNSE chauhan",
    classifiers=[
        "License :: OSI Approved :: IISc License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        # Add more classifiers here
    ],
    packages=setuptools.find_packages(),
    install_requires=[
        "customtkinter",
        "tk",
        "mcculw",
        "opencv-python",
        "numpy",
        "pillow",
        "setuptools",
        "wheel",
        "darkdetect"
        # Add other dependencies here
    ]
    
)