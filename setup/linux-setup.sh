#!/bin/bash
# Copyright 2017 Kevin Froman - MIT License - https://ChaosWebs.net/
E=$(tput sgr0);    R=$(tput setab 1); G=$(tput setab 2); Y=$(tput setab 3);
B=$(tput setab 4); M=$(tput setab 5); C=$(tput setab 6); W=$(tput setab 7);
function e() { echo -e "$E"; }
function x() { echo -n "$E  "; }
function r() { echo -n "$R  "; }
function g() { echo -n "$G  "; }
function y() { echo -n "$Y  "; }
function b() { echo -n "$B  "; }
function m() { echo -n "$M  "; }
function c() { echo -n "$C  "; }
function w() { echo -n "$W  "; }

#putpixels
function u() { 
    h="$*";o=${h:0:1};v=${h:1}; 
    for i in `seq $v` 
    do 
        $o;
    done 
}

img="\
x40 e1 x40 e1 x40 e1 x40 e1 x40 e1 x40 e1 x5 b7 x4 b6 x18 e1 x8 b1 x7 b1 x23 e1 x8 b1 x7 b1 x23 e1 x8 b1 x7 b1 x2 b3 x18 e1 x8 b1 x7 b1 x4 b1 x18 e1 x8 b1 x7 b1 x4 b1 x18 e1 x8 b1 x7 b6 x18 e1 x40 e1 x40 e1 x40 e1 x40 e1 x40 e1 x40 e1 x40 e1 x40 e1 x40 e1 x40"

for n in $img
do
    u $n
done
e;
read -p "Install Tinygen to current directory? y/n" -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]
then
    echo "Installing dependencies"
    sudo apt-get install git python3 python3-pip
    if [ "$?" != "0" ]; then
        echo "Failed to install dependencies. Installation failed"
        exit 1
    fi
    echo "Installing Python markdown"
    sudo pip3 install markdown
    if [ "$?" != "0" ]; then
        echo "Failed to install Python markdown"
        echo "Python Markdown is optional, so installation will continue"
    fi
    echo "Cloning TinyGen git repo"
    git clone https://github.com/beardog108/tinygen.git .
    if [ "$?" != "0" ]; then
        echo "Failed to clone repo. Installation failed"
        exit 1
    fi
else
    echo "not installing"
fi
