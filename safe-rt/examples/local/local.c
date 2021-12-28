
void mod(int* addr, int num) {
    *addr = num;
}

int main() {
    int hello = 0;
    mod(&hello, 100);
}
