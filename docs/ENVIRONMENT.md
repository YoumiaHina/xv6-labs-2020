# Reproducible environment

## Installed platform

| Component | Version |
|---|---|
| WSL | 2.6.3 |
| Linux kernel | 6.6.87.2 |
| Distribution | Ubuntu 24.04 LTS |
| RISC-V GCC | 13.2.0 |
| QEMU | 8.2.2 |
| GDB multiarch | 15.1 |

The WSL distribution is named `Ubuntu-24.04` and its default user is `xv6`.
The source-of-truth build trees are kept under `/home/xv6/work`; the portfolio
clone exposed to Windows is at `/mnt/e/xv6/xv6-labs-2020`.

## Packages

```sh
apt-get install -y \
  git build-essential gdb-multiarch qemu-system-misc \
  gcc-riscv64-linux-gnu binutils-riscv64-linux-gnu \
  gcc-riscv64-unknown-elf binutils-riscv64-unknown-elf \
  python3 python3-pip python-is-python3
```

## Ubuntu 24.04 compatibility

The Fall 2020 starter code predates GCC 13, recent binutils, and QEMU's PMP
enforcement. Every solution branch therefore includes these environment-only
changes:

1. Add `-Wno-infinite-recursion` to `CFLAGS`; xv6's shell dispatcher is
   intentionally recursive and GCC 13 otherwise turns that diagnostic into an
   error through `-Werror`.
2. Export `_entry` with `.globl _entry`; current binutils requires the ELF entry
   symbol to be global.
3. Configure one PMP entry covering physical memory before `mret`; QEMU 8
   otherwise raises an instruction-access fault on the first supervisor-mode
   instruction.

These adjustments are kept separate in commit messages and do not implement
any lab requirement.

## Verification

```sh
riscv64-unknown-elf-gcc --version
qemu-system-riscv64 --version
cd /mnt/e/xv6/xv6-labs-2020
git switch sol-util
make clean
make qemu
```

Successful boot ends with `init: starting sh` and an xv6 `$` prompt.

