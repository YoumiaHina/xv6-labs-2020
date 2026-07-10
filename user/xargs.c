#include "kernel/types.h"
#include "kernel/stat.h"
#include "kernel/param.h"
#include "user/user.h"

#define LINE_SIZE 512

static int
runline(char *line, int length, int argc, char *argv[])
{
  char *args[MAXARG];
  int narg = 0;
  int i;

  for(i = 1; i < argc; i++){
    if(narg == MAXARG - 1){
      fprintf(2, "xargs: too many arguments\n");
      return -1;
    }
    args[narg++] = argv[i];
  }

  i = 0;
  while(i < length){
    while(i < length && (line[i] == ' ' || line[i] == '\t'))
      i++;
    if(i == length)
      break;
    if(narg == MAXARG - 1){
      fprintf(2, "xargs: too many arguments\n");
      return -1;
    }
    args[narg++] = &line[i];
    while(i < length && line[i] != ' ' && line[i] != '\t')
      i++;
    if(i < length)
      line[i++] = 0;
  }
  if(narg == argc - 1)
    return 0;
  args[narg] = 0;

  int pid = fork();
  if(pid < 0){
    fprintf(2, "xargs: fork failed\n");
    return -1;
  }
  if(pid == 0){
    exec(args[0], args);
    fprintf(2, "xargs: exec %s failed\n", args[0]);
    exit(1);
  }
  wait(0);
  return 0;
}

int
main(int argc, char *argv[])
{
  char line[LINE_SIZE];
  int length = 0;
  char c;
  int n;

  if(argc < 2){
    fprintf(2, "usage: xargs command [initial-arguments ...]\n");
    exit(1);
  }

  while((n = read(0, &c, 1)) == 1){
    if(c == '\n'){
      line[length] = 0;
      if(runline(line, length, argc, argv) < 0)
        exit(1);
      length = 0;
    } else if(length == sizeof(line) - 1){
      fprintf(2, "xargs: input line too long\n");
      exit(1);
    } else {
      line[length++] = c;
    }
  }
  if(n < 0){
    fprintf(2, "xargs: read failed\n");
    exit(1);
  }
  if(length > 0){
    line[length] = 0;
    if(runline(line, length, argc, argv) < 0)
      exit(1);
  }
  exit(0);
}
