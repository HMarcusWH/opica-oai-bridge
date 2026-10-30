.PHONY: preflight test prepare bootstrap resolve cache oai zeta smoke all axioms comparator provenance clean-generated

preflight:
	python3 scripts/verify_lock.py

test:
	python3 -m unittest discover -s tests -v

prepare:
	python3 scripts/prepare_workspace.py

bootstrap: prepare
	bash scripts/build.sh smoke

resolve:
	bash scripts/build.sh resolve

cache:
	bash scripts/build.sh cache

oai:
	bash scripts/build.sh oai

zeta:
	bash scripts/build.sh zeta

smoke:
	bash scripts/build.sh smoke

all:
	bash scripts/build.sh full

axioms:
	bash scripts/build.sh axioms

comparator:
	bash scripts/verify_comparator.sh

provenance:
	python3 scripts/provenance_report.py

clean-generated:
	@echo 'Generated workspace is never automatically deleted: inspect .bridge/ and symlinks before removal.'
