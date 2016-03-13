JSON ?= example.json

gen_chisel:
	python apb-bridge.py --json=$(JSON)  --outdir=chisel

gen_v:
	cd chisel && sbt "run --genHarness --backend v"

all:  gen_chisel gen_v


.PHONY: gen_chisel gen_v
