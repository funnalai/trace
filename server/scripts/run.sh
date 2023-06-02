#!/bin/bash

prisma generate
prisma db push
make server