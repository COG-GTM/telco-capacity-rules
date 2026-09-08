CXX ?= g++
CXXFLAGS ?= -std=c++17 -O2 -Wall -Wextra

vectors_inc = tests/vectors.inc
billing_vectors_inc = tests/billing_vectors.inc
billing_invoice_vectors_inc = tests/billing_invoice_vectors.inc

$(vectors_inc): tests/gen_vectors.py ../spec/vectors.json
	python3 tests/gen_vectors.py

vectors_test: tests/vectors_test.cpp $(vectors_inc) include/telco_capacity/capacity.h
	$(CXX) $(CXXFLAGS) -Iinclude -Itests -o $@ tests/vectors_test.cpp

$(billing_vectors_inc): tests/gen_billing_vectors.py ../spec/billing_rule_vectors.json
	python3 tests/gen_billing_vectors.py

$(billing_invoice_vectors_inc): tests/gen_billing_invoice_vectors.py ../spec/billing_vectors.json
	python3 tests/gen_billing_invoice_vectors.py

billing_vectors_test: tests/billing_vectors_test.cpp $(billing_vectors_inc) $(billing_invoice_vectors_inc) include/telco_rules/billing.h
	$(CXX) $(CXXFLAGS) -Iinclude -Itests -o $@ tests/billing_vectors_test.cpp

test: vectors_test billing_vectors_test
	./vectors_test
	./billing_vectors_test

.PHONY: test clean

clean:
	rm -f vectors_test billing_vectors_test tests/vectors.inc tests/billing_vectors.inc tests/billing_invoice_vectors.inc
