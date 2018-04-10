
# global config
BASEDIR=./binaries/ChakraCore
PLATFORM=darwin
INPUT=./test/PyChakra.test.cc
OUTPUT=./dist/PyChakra.test

IDIR=$(BASEDIR)/include
CC=gcc

ifeq (darwin, ${PLATFORM})
LDIR=$(BASEDIR)/lib/libChakraCore.dylib
ICU4C_LIBRARY_PATH ?= /usr/local/opt/icu4c
CFLAGS=-lstdc++ -std=c++11 -I$(IDIR) -g
FORCE_STARTS=-Wl,-force_load,
FORCE_ENDS=
LIBS=-framework CoreFoundation -framework Security -lm -ldl -Wno-c++11-compat-deprecated-writable-strings \
	-Wno-deprecated-declarations -Wno-unknown-warning-option -o $(OUTPUT)
LDIR+=$(ICU4C_LIBRARY_PATH)/lib/libicudata.a \
	$(ICU4C_LIBRARY_PATH)/lib/libicuuc.a \
	$(ICU4C_LIBRARY_PATH)/lib/libicui18n.a
else
LDIR=$(BASEDIR)/lib/libChakraCore.so
CFLAGS=-lstdc++ -std=c++0x -I$(IDIR) -g
FORCE_STARTS=-Wl,--whole-archive
FORCE_ENDS=-Wl,--no-whole-archive
LIBS=-pthread -lm -ldl -licuuc -Wno-c++11-compat-deprecated-writable-strings \
	-Wno-deprecated-declarations -Wno-unknown-warning-option -o $(OUTPUT)
endif

.PHONY: test

test:
	@ make build
	@ ./$(OUTPUT)
	@ make clean

.PHONY: clean

build:
	@ $(CC) $(INPUT) $(CFLAGS) $(FORCE_STARTS) $(LDIR) $(FORCE_ENDS) $(LIBS)

clean:
	@ rm $(OUTPUT)
