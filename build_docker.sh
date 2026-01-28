#!/bin/bash
NAMESPACE="${1:-codebase_b1880_app}"
docker build -t "$NAMESPACE" .