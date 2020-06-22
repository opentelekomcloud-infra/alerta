#!/bin/bash
DIR=$PWD
LDAP_LIB=basic_ldap.py
LDAP_PATH=$(find /venv -name $LDAP_LIB 2> /dev/null|head -1)
if [ -n "$LDAP_PATH" ];then
   LDAP_BASE=$(dirname $LDAP_PATH)
   cd $LDAP_BASE && patch < $DIR/basic_ldap.patch
fi
