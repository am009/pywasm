int b = 0;

int add(int a) {
    return a + b;
}

void mod(int new) {
    b = new;
}

int main() {
    mod(128);
    return 0;
}