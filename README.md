# EEG_Brain_Model
2024/2025 Capstone project EEG Brain Model

## About This Project
- This project is used to run a physical brain model that hosts an ESP32 microcontroller along with an accompanying app.  

## Installation
``` pip install kivy```
``` pip install kivymd```

## Dependencies
- [Kivy](https://github.com/kivy/kivy) >= 2.3.0 ([Installation](https://kivy.org/doc/stable/gettingstarted/installation.html))
- [Python 3.7+](https://www.python.org/)
- [Java OpenJDK8](https://www.openlogic.com/openjdk-downloads)

## How to Build with Buildozer

#### On Linux
- Use Buildozer [directly](https://github.com/kivy/buildozer#installing-buildozer-with-target-python-3-default) 
  or via [Docker](https://github.com/kivy/buildozer/blob/master/Dockerfile).

#### On Windows
- Install [Ubuntu WSL](https://ubuntu.com/wsl) and follow [Linux steps](#On-Linux).


Do not forget to run `buildozer android clean` before building if version was updated.

## Documentation
- See documentation for kivymd at https://kivymd.readthedocs.io
- See documentation for Java OpenJDK8 at https://docs.datastax.com/en/jdk-install/doc/jdk-install/installOpenJdkDeb.html
- See documentation for Buildozer at https://buildozer.readthedocs.io/en/latest/quickstart.html
