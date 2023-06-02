#!/bin/bash

poetry install
prisma generate
prisma db push
make server