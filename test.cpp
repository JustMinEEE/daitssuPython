#include <stdio.h>

int main(void)
{
	char name[3][10];
	int age[3];
	float height[3];

	for (int i = 0; i < 3; i++) {
		printf("%d번째 사람의 이름, 나이, 키를 입력하세요: ", i);
		scanf_s("%s %d %f", name[i], (unsigned int)sizeof(name[i]), &age[i], &height[i]);
	}

	float avgAge = 0;
	float avgHei = 0;

	for (int i = 0; i < 3; i++) {
		avgAge += age[i];
		avgHei += height[i];
	}
	avgAge /= 3;
	avgHei /= 3;

	printf("평균 나이: %.2f\n평균 키: %.2f\n", avgAge, avgHei);

	for (int i = 0; i < 3; i++) {
		if (age[i] > avgAge) {
			printf("평균 나이보다 많은 사람: %s\n", name[i]);
		}
		if (height[i] > avgHei) {
			printf("평균 키보다 많은 사람: %s\n", name[i]);
		}
	}

	return 0;
}
