
unsigned char gc = 255;

void mod(unsigned short *addr, int num) {
    *addr =  num;
}

int main () {
    unsigned short lc = 15535;
    mod(&lc, 65535);
}
