#!/bin/bash

g++ -o a.out 2105044.cpp -lpthread

./a.out $1 $2 

rm -rf a.out
