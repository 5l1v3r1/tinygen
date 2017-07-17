# TinyGen

A simple website and blog generator written in Python

Work in progress, but basic features done.

**TinyGen is in early stages. It is not ready for production use**

Tested on Linux and Windows

## Installation

### Linux & Mac


#### Debian Based Distros

There is an installation script for Debian (verified for Jessie & Stretch). It should also work for other Debian-based distros.

Download and run the script: `wget https://raw.githubusercontent.com/beardog108/tinygen/master/setup/linux-setup.sh && chmod +x linux-setup.sh && ./linux-setup.sh`

#### Other Linux and Mac

* Install git with your system package manager if needed
* Install Python 3 and python3-pip with your system package manager
* Install Python Markdown with pip
* Clone this repo

### Windows

* Install Git
* Install Python 3 and python3-pip
* Install Python Markdown with pip
* Clone this repo

## Current features:

* ✅ Less than 950 lines of code
* ✅ Generates light weight but readable HTML. 
* ✅ No JavaScript by default (you can still use JS if you like though)
* ✅ Theme system
* ✅ Plugin system with API (currently undocumented)
* ✅ Markdown and HTML support
* ✅ RSS feed for blog
* ✅ Built in web server for testing
* ✅ Draft system


## To do list:

- [x] Static blog support
- [x] Compatibility with Windows & most *nix distros
- [x] Better output with color support
- [x] Plugin support
- [x] Theme support
- [x] Built in web server (for testing purposes)
- [x] Markdown support
- [ ] Publish to free site hosting server
- [x] RSS Blog Feeds
- [ ] Document the code, plugin API, and theme system

# Reporting issues

When filing an issue please:

* Check for similar existing issues, both closed and open
* Take screenshots if helpful in the context
* Report Tinygen, Python, and OS version (and if a html/css bug, browser version(s))
* Be respectful, and try to use good english (if English is not your first language, I will be patient, but please try.)

# Contributing

I welcome well made pull requests, but please get in touch with me first if you want to do non-trivial changes.

Also consider if your feature would be better suited as a plugin or theme
