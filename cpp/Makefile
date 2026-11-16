CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra
PYTHON ?= python3

.PHONY: test clean

test: unit_test vectors_test
	./unit_test
	./vectors_test

vectors_inc = tests/vectors.inc

$(vectors_inc): tests/gen_vectors.py ../spec/vectors.json
	$(PYTHON) tests/gen_vectors.py

unit_test: tests/unit_test.cpp include/telco_capacity/capacity.h
	$(CXX) $(CXXFLAGS) -Iinclude -o $@ tests/unit_test.cpp

vectors_test: tests/vectors_test.cpp $(vectors_inc) include/telco_capacity/capacity.h
	$(CXX) $(CXXFLAGS) -Iinclude -Itests -o $@ tests/vectors_test.cpp

clean:
	rm -f unit_test vectors_test tests/vectors.inc
