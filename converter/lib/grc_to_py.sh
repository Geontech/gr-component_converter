#!/bin/bash

##################################################
# File: grc_to_py.sh
# Author: Chris Conover
# Description: A shell script that handles
#              generating a python file using
#              "grcc" on a passed GRC file
# Created: Wed July 13 10:00:00 2017
##################################################

# ##############################################################################
# This simple shell script is used to generate a brand new python executable
# without invoking the GNURadio IDE for a user-provided GRC file. The script
# will first search if a compiled versions of the user-passed GRC file already
# exists (not nescessarily under the same name), then will proceed with either
# creating a new file, replacing and old, or exiting at the user's discretion.
# ##############################################################################

# TODO: MAKE SURE TO CHANGE CODE BACK TO REPRESENT THE GRCC EXECUTION FOR
# A UBUNTU BASED INSTALLATION (NOT USING PYBOMBS).

# TODO: When made into executuable, consider using "chmod 755 ___" because this
# command gives the developer read, write, and execution permissions, while it
# gives users only read and execute permissions.

# TODO: Find a way to silence the following GNURadio Companion Warning:
# >>> Warning: This flow graph may not have flow control: no audio or RF hardware blocks found. Add a Misc->Throttle block to your flow graph to avoid CPU congestion.

# TODO: Change the overwrite check to do its search based on the name of the
# python file that the GRC would produce, not the name of the .grc replaced
# with .py

grc_file=$1
generated_py_file=$2
output_dir=$3
temp=$4
trimmed=$5

output_temp="${output_dir}/${temp}"
output_trimmed="${output_dir}/${trimmed}"

# TODO: Could potentially create a new directory to place generated file within.
# TODO: Add an option for renaming the newly created Python file instead of
# replacing the old Python file (with the same name) completely. (Not sure if
# this would ever be useful...)

# BASEDIR=$(dirname $0)
# grcc --directory=${BASEDIR} $grc_file

if [ ! -f "$generated_py_file" ]
  then
    source ~/prefix/setup_env.sh
    grcc --directory=$output_dir $grc_file
    touch $output_temp $output_trimmed                                          # Temporary files have to be created here due to subprocess working directory restrictions??

else

  echo "The file \"$generated_py_file\" (compiled from: \"$grc_file\") already exists. Do you wish to replace it? (Y/N): "

  while [ True ]
  do

    read -n 1 -s response
    uresponse="$(echo $response | tr "[a-z]" "[A-Z]")"                          # Converting any lowercase input to uppercase

    if [ "$uresponse" = "N" ]
      then
        echo "Exiting without replacing file \"$generated_py_file\""
        exit                                                                    # Not sure that this is good style
    elif [ "$uresponse" = "Y" ]
      then
        rm $generated_py_file
        source ~/prefix/setup_env.sh
        grcc --directory=$output_dir $grc_file
        touch $output_temp $output_trimmed
        exit
    else
      echo "Error: Invalid character option."
      echo "Please enter \"Y\" to replace existing file, or \"N\" to cancel: "
    fi

  done
fi
