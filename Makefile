.PHONY: help test install clean serve

help:		## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN {FS = ":.*?## "}; {printf "  %-12s %s\n", $$1, $$2}'

test:		## Run the offline test suite (no network beyond loopback)
	cd .. && python -m unittest discover -s tinyapi/tests -t . -v

install:	## Editable install of the package
	pip install -e .

serve:		## Run the bundled tasks API: make serve ARGS='--port 8000'
	python -m tinyapi $(ARGS)

clean:		## Remove caches and build artifacts
	find . -type d -name __pycache__ -prune -exec rm -rf {} + 2>/dev/null || true
	rm -rf *.egg-info build dist .eggs *.db
