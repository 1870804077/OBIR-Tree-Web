#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#define N 10000

// 生成-90~90的随机纬度
double random_latitude() {
    return ((double)rand() / RAND_MAX) * 180.0 - 90.0;
}

// 生成-180~180的随机经度
double random_longitude() {
    return ((double)rand() / RAND_MAX) * 360.0 - 180.0;
}

int main() {
    FILE *fp = fopen("data.txt", "w");
    if (!fp) {
        printf("无法创建文件！\n");
        return 1;
    }
    srand((unsigned)time(NULL));
    for (int i = 0; i < N; ++i) {
        int id = 372 + (i % 200) + (i / 200) * 10000;
        fprintf(fp, "%d 文本%d_copy%d %.6f %.6f\n",
            id,
            (i % 200) + 1,
            i / 200,
            random_latitude(),
            random_longitude()
        );
    }
    fclose(fp);
    printf("已生成10000条数据到 data.txt\n");
    return 0;
}