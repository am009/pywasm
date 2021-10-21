
// 展示如何从内存地址找到变量类型

extern void exame(char * c);

void use_func(int *a) {
    exame( ((char*)a) + 1 );
}

int main() {
    int a;
    use_func(&a);
    return 0;
}
