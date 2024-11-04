#!/bin/bash

if [ -z "$1" ] || [ -z "$2" ]; then
    echo "Usage: $0 <playbook-name> <inventory-name>"
    exit 1
fi

ansible-playbook playbooks/$1 -i inventory/$2