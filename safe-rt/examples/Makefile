.PHONY: all clean
all: $(addsuffix .wasm, $(basename $(wildcard *.c))) $(addsuffix .wat, $(basename $(wildcard *.c))) $(addsuffix .wasm.dwarferdump, $(basename $(wildcard *.c))) $(addsuffix .wasm.dwarfdump, $(basename $(wildcard *.c)))

%.wasm: %.c
	# emcc --no-entry ./$< -g -o ./$@
	clang-12 --target=wasm32 --no-standard-libraries -Wl,--export-all -Wl,--no-entry -g -o ./$@ ./$<

%.wat: %.wasm
	wasm2wat ./$< > ./$@

%.wasm.dwarfdump: %.wasm
	llvm-dwarfdump -all ./$< > ./$@

%.wasm.dwarferdump: %.wasm
	python3 ./dwarfer.py ./$< > ./$@

clean:
	rm *.wasm *.wat *.wasm.dwarfdump *.wasm.dwarferdump
