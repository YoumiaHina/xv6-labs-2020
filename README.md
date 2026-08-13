# MIT 6.S081 Fall 2020 - xv6 Labs

This private repository contains the completed course-project work for all
eleven MIT 6.S081 Fall 2020 xv6 labs. Each solution lives on an independent
branch based on the matching upstream lab branch; the branches are intentionally
not merged into one kernel because MIT distributes a different starter tree for
each lab. All official grading suites pass, for a combined **985/985**.

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
| 1 | Unix utilities | [`sol-util`](https://github.com/YoumiaHina/xv6-labs-2020/tree/sol-util) | Verified: 100/100 |
| 2 | System calls | [`sol-syscall`](https://github.com/YoumiaHina/xv6-labs-2020/tree/sol-syscall) | Verified: 35/35 |
| 3 | Page tables | [`sol-pgtbl`](https://github.com/YoumiaHina/xv6-labs-2020/tree/sol-pgtbl) | Verified: 66/66 |
| 4 | Traps | [`sol-traps`](https://github.com/YoumiaHina/xv6-labs-2020/tree/sol-traps) | Verified: 85/85 |
| 5 | Lazy allocation | [`sol-lazy`](https://github.com/YoumiaHina/xv6-labs-2020/tree/sol-lazy) | Verified: 119/119 |
| 6 | Copy-on-write | [`sol-cow`](https://github.com/YoumiaHina/xv6-labs-2020/tree/sol-cow) | Verified: 110/110 |
| 7 | Multithreading | [`sol-thread`](https://github.com/YoumiaHina/xv6-labs-2020/tree/sol-thread) | Verified: 60/60 |
| 8 | Locks | [`sol-lock`](https://github.com/YoumiaHina/xv6-labs-2020/tree/sol-lock) | Verified: 70/70 |
| 9 | File system | [`sol-fs`](https://github.com/YoumiaHina/xv6-labs-2020/tree/sol-fs) | Verified: 100/100 |
| 10 | mmap | [`sol-mmap`](https://github.com/YoumiaHina/xv6-labs-2020/tree/sol-mmap) | Verified: 140/140 |
| 11 | Network driver | [`sol-net`](https://github.com/YoumiaHina/xv6-labs-2020/tree/sol-net) | Verified: 100/100 |

The acceptance gate for every branch was the official `make grade` suite plus
the lab-specific tests documented on the [MIT 2020 course
site](https://pdos.csail.mit.edu/6.828/2020/xv6.html). Each final branch was
then cloned into a clean verification directory and graded again.

## Running a lab

From Ubuntu WSL2:

```sh
cd /mnt/e/xv6/xv6-labs-2020
git switch sol-util             # choose the requested lab
make clean
make grade
```

For interactive use, run `make qemu`. Exit QEMU with `Ctrl-a x`.

## Project report

- [Complete Chinese experiment report (DOCX)](deliverables/xv6及Labs课程项目实验报告（MIT2020）.docx)
