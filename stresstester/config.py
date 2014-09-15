#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import with_statement
import yaml
import os

# Bonjour resolving
MCP_METHODS_SERVICE = 'fi.iki.rambo.stresser.mcp'
MCP_SIGNALS_SERVICE = 'fi.iki.rambo.stresser.mcp.signals'
LOG_METHODS_SERVICE = 'fi.iki.rambo.stresser.logger'

MCP_METHODS_PORT = 7070
MCP_SIGNALS_PORT = 7071
LOG_METHODS_PORT = 7080
LOG_SIGNALS_PORT = 7081

YAML_CONFIG_FILE = 'config.yml'
YAML_CONFIG = {}
if os.path.exists(YAML_CONFIG_FILE):
    with open(YAML_CONFIG_FILE) as f:
        YAML_CONFIG = yaml.load(f)

#print YAML_CONFIG
