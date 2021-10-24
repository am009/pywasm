
int arrg[10] = {1,3,4,5,6};

void mod(int* arr, int num) {
    arrg[9] = 100;
    arr[2] = num;
}

int main() {
    int arr[4] = {1,2,99,4};
    mod(arr, 100);
}
