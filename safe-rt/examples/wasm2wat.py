
import sys

import pywasm

pywasm.binary.wasm2wat(sys.argv[1], sys.argv[2])
