int b = 0;

void mod1(int new) {
    b = new;
}

int main() {
    mod1(128);
    return 0;
}

// ===============local=========

void mod2(int* addr, int num) {
    *addr = num;
}

int main2() {
    int hello = 0;
    mod2(&hello, 100);
    return 0;
}

// =============array===========

int arrg[10] = {1,3,4,5,6};

void mod3(int* arr, int num) {
    arrg[9] = 100;
    arr[2] = num;
}

int main3() {
    int arr[4] = {1,2,99,4};
    mod3(arr, 100);
    return 0;
}