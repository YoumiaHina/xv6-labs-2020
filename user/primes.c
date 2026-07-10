#include "kernel/types.h"
#include "kernel/stat.h"
#include "user/user.h"

static void
sieve(int left)
{
  int prime;
  int number;
  int right[2];

  if(read(left, &prime, sizeof(prime)) != sizeof(prime)){
    close(left);
    exit(0);
  }
  printf("prime %d\n", prime);

  if(pipe(right) < 0){
    fprintf(2, "primes: pipe failed\n");
    exit(1);
  }
  int pid = fork();
  if(pid < 0){
    fprintf(2, "primes: fork failed\n");
    exit(1);
  }
  if(pid == 0){
    close(left);
    close(right[1]);
    sieve(right[0]);
  }

  close(right[0]);
  while(read(left, &number, sizeof(number)) == sizeof(number)){
    if(number % prime != 0 &&
       write(right[1], &number, sizeof(number)) != sizeof(number)){
      fprintf(2, "primes: write failed\n");
      exit(1);
    }
  }
  close(left);
  close(right[1]);
  wait(0);
  exit(0);
}

int
main(int argc, char *argv[])
{
  int first[2];

  if(argc != 1){
    fprintf(2, "usage: primes\n");
    exit(1);
  }
  if(pipe(first) < 0){
    fprintf(2, "primes: pipe failed\n");
    exit(1);
  }

  int pid = fork();
  if(pid < 0){
    fprintf(2, "primes: fork failed\n");
    exit(1);
  }
  if(pid == 0){
    close(first[1]);
    sieve(first[0]);
  }

  close(first[0]);
  for(int number = 2; number <= 35; number++){
    if(write(first[1], &number, sizeof(number)) != sizeof(number)){
      fprintf(2, "primes: write failed\n");
      exit(1);
    }
  }
  close(first[1]);
  wait(0);
  exit(0);
}
