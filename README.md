# MIT 6.S081 Fall 2020 - xv6 Labs

This private repository contains the course-project work for all eleven MIT
6.S081 Fall 2020 xv6 labs. Each solution lives on an independent branch based
on the matching upstream lab branch; the branches are intentionally not merged
into one kernel because MIT distributes a different starter tree for each lab.

## Environment

- Windows Subsystem for Linux 2
- Ubuntu 24.04 LTS
- RISC-V GCC 13.2
- QEMU 8.2
- Python 3 grading scripts

Ubuntu 24.04 needs three compatibility-only adjustments on every solution
branch: suppress GCC's `infinite-recursion` diagnostic for xv6's recursive
shell dispatcher, export `_entry` as a global symbol, and configure PMP before
entering supervisor mode. These changes do not alter the lab behavior.

## Lab branches

| # | Lab | Solution branch | Status |
|---:|---|---|---|
| 1 | Unix utilities | `sol-util` | In progress |
| 2 | System calls | `sol-syscall` | In progress |
| 3 | Page tables | `sol-pgtbl` | In progress |
| 4 | Traps | `sol-traps` | In progress |
| 5 | Lazy allocation | `sol-lazy` | In progress |
| 6 | Copy-on-write | `sol-cow` | In progress |
| 7 | Multithreading | `sol-thread` | In progress |
| 8 | Locks | `sol-lock` | In progress |
| 9 | File system | `sol-fs` | In progress |
| 10 | mmap | `sol-mmap` | In progress |
| 11 | Network driver | `sol-net` | In progress |

The acceptance gate for every branch is the official `make grade` suite plus
the lab-specific tests documented on the [MIT 2020 course
site](https://pdos.csail.mit.edu/6.828/2020/xv6.html).

## Running a lab

From Ubuntu WSL2:

```sh
cd /mnt/e/xv6/xv6-labs-2020
git switch sol-util             # choose the requested lab
make clean
make grade
```

For interactive use, run `make qemu`. Exit QEMU with `Ctrl-a x`.

## Project documentation

- [Experiment report template](docs/REPORT_TEMPLATE.md)
- [Defense runbook](docs/DEFENSE_RUNBOOK.md)
- [Reproducible environment notes](docs/ENVIRONMENT.md)

