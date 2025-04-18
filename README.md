# CPU Tracker

Welcome to the CPU Tracker repository! This project is designed to keep track of electornic parts.

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Contributing](#contributing)
- [License](#license)

## Introduction

CPU Tracker is a personal tool to keep track of parts received, inspected and tested with all the information gathered along the way. Mostly to find and ease access to information and extract data for reports etc...

## Features

- Web interface .
- Should run on any modern browser, mostly tested on Chrome.
- Conteinerized

## Requirements

** Docker
** Create a folder called "certs" for your self signed certificates

    ```sh

openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout certs/localhost.key -out certs/localhost.crt -subj "/CN=localhost"

## Installation

1.  **Clone the Repository**: Clone this repository to your local machine using the following command:

    ```sh
    git clone https://github.com/arielrivera/cputracker.git

    ```

2.  **Docker**: Make sure you're running Docker in your system.

3.  **Build container and run the app**:

    On Mac / Linux
    First run or rebuilding if you make changes, run :

        ./flarebrun.sh (Change your shell if you're not in a modern MacOs or not using szh).

        If only re-running the container without changes , just run the container again.

    -On windows:
    --First time run or rebuilding if you make changes, run :

        .\full_path\winFullBuildRun.bat

    --If only re-running the container once it has been build then use:

        \full_path\winSimpleRin.bat or just start the container using the Docker GUI etc...

4.  **Open the Web UI**:
    -The script is defaulted to the local system's IP and :5001 port
    -Open Chrome or Firefox and navigate to http://127.0.0.1:5001 for example.

## Usage

- Click around...
- As in any other docker image, docker exec -it cputrackerapp sh

## License

- Private use only

```

```
