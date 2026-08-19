default:
	@echo "possible rules:"
	@echo
	@echo "  clean - remove processing files"
	@echo ""
	@echo ""
	@echo ""
clean:
	rm -f {month,speed}*summary*.{xls,dat,gp}

CFLAGS += -Wall
CFLAGS += -Wimplicit
CFLAGS += -W
CFLAGS += -Wredundant-decls

CXXFLAGS += -Wall
CXXFLAGS += -Wimplicit
CXXFLAGS += -W
CXXFLAGS += -Wredundant-decls

ais_filter_by_mmsi: ais_filter_by_mmsi.cxx
	g++ $< -o $@ ${CXXFLAGS} -O3 -funroll-loops -fexpensive-optimizations -DNDEBUG
