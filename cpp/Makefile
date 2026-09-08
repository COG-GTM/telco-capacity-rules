CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra

.PHONY: test clean

test: vectors_test
	./vectors_test

vectors.inc: tests/gen_vectors.py ../spec/vectors.json
	python3 tests/gen_vectors.py

vectors_test: tests/vectors_test.cpp vectors.inc include/telco_capacity/capacity.h
	$(CXX) $(CXXFLAGS) -Iinclude -Itests -o $@ tests/vectors_test.cpp

clean:
	rm -f vectors_test tests/vectors.inc
