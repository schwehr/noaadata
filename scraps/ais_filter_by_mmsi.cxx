// Since: 18-Apr-2010
// Kurt Schwehr
// License: LGPL v3
// g++ ais_filter_by_mmsi.cxx -o ais_filter_by_mmsi -Wall -O3 -funroll-loops -fexpensive-optimizations 

#include <fstream>
#include <iostream>
#include <bitset>
#include <string>
#include <cassert>
#include <sstream>
#include <vector>
#include <set>

using namespace std;

const size_t max_bits = 168+4*256;
//const size_t max_bits = 168;

// http://stackoverflow.com/questions/236129/c-how-to-split-a-string
std::vector<std::string> &split(const std::string &s, char delim, std::vector<std::string> &elems) {
    std::stringstream ss(s);
    std::string item;
    while(std::getline(ss, item, delim)) {
        elems.push_back(item);
    }
    return elems;
}

std::vector<std::string> split(const std::string &s, char delim) {
    std::vector<std::string> elems;
    return split(s, delim, elems);
}

void print_bits(bitset<max_bits> &bits) {
    for (size_t i=0; i < max_bits; i++) cout << bits[i]; cout << endl;
    for (size_t i=0; i < max_bits; i++) cout << i%10;    cout << endl;
}

void print_bits6(bitset<6> &bits) { 
    for (size_t i=0; i<6; i++) cout << (bits[i]?"1":"0"); 
}

int decode_message_id(bitset<max_bits> &msg_bits) {
    bitset<6> bits;
    for (size_t i=0; i < 6; i++)
        bits[i] = msg_bits[5-i];
    return bits.to_ulong();
}

int decode_mmsi(bitset<max_bits> &msg_bits) {
    bitset<30> bits;
    for (size_t i=0; i < 30; i++)
        bits[i] = msg_bits[8 + 29-i];
    return bits.to_ulong();
}

bitset<6> nmea_ord[128]; // Direct lookup by the character ord number (ascii)

void build_nmea_lookup() {
    for (int c=0; c < 128; c++) {
        int val = c - 48;
        if (val>=40) val-= 8;
        if (val < 0) continue;
        bitset<6> bits(val);
        bool tmp;
        tmp = bits[5]; bits[5] = bits[0]; bits[0] = tmp;
        tmp = bits[4]; bits[4] = bits[1]; bits[1] = tmp;
        tmp = bits[3]; bits[3] = bits[2]; bits[2] = tmp;
        nmea_ord[c] = bits;
    }
}

void splice_bits(bitset<max_bits> &dest, bitset<6> src, size_t start) {
    for (size_t i=0; i<6; i++) { dest[i+start] = src[i]; }
}

void aivdm_to_bits(bitset<max_bits> &bits, const string &nmea_payload) {
    for (size_t i=0; i < nmea_payload.length(); i++)
        splice_bits(bits, nmea_ord[int(nmea_payload[i])], i*6);
}


int main(size_t argc, char *argv[]) {
    build_nmea_lookup();
    //cout << "argc: " << argc << endl;
    assert(2<=argc);
    ifstream infile(argv[1]);
    if (! infile.is_open() ) {
        cerr << "Unable to open file: " << argv[1] << endl;
        exit(1);
    }

    set<int> mmsi_set;
    cout.flush();
    for (size_t i=2; i < argc; i++) {
        const int mmsi = atoi(argv[i]);
        mmsi_set.insert(mmsi);
    }
#if 0
    cerr << "mmsi_set:" << endl;
    for (set<int>::iterator i=mmsi_set.begin(); i != mmsi_set.end(); i++) {
        cerr << "\t" << *i << endl;
    }
#endif

    bitset<max_bits> bs;
    int i=0;
    string line;
    while (!infile.eof()) {
        i++;
        getline(infile,line);

        if (line.length() < 20) {continue;}
        if ('!' != line[0]  ||  'A' != line[1] ) {continue;}
        vector<string> fields = split(line,',');
        {
            if (fields.size() < 7) continue;
            aivdm_to_bits(bs, fields[5]);
            const int mmsi = decode_mmsi(bs);
            if (mmsi_set.find(mmsi) == mmsi_set.end()) continue;
            cout << line << "\n";
        }
    }

    return 0;
}
