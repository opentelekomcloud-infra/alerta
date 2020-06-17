#!/bin/bash
LDAP_LIB=basic_ldap.py
LDAP_PATH=$(find /venv -name $LDAP_LIB 2> /dev/null|head -1)
if [ -n "$LDAP_PATH" ];then
  cp basic_ldap.py $LDAP_PATH
fi
