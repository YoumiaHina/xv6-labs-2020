# Defense runbook

## Preflight

1. Start Ubuntu 24.04 WSL2 and verify `riscv64-unknown-elf-gcc --version` and
   `qemu-system-riscv64 --version`.
2. Fetch the private GitHub repository and confirm the working tree is clean.
3. Run `make clean && make grade` on every solution branch before the defense.
4. Keep two WSL terminals ready for the network lab's host server and QEMU.

## Live demonstration pattern

```sh
cd /mnt/e/xv6/xv6-labs-2020
git switch sol-LAB
make clean
make qemu
```

Inside xv6, run the lab-specific test requested by the examiner. Exit with
`Ctrl-a x`. For the network lab, start `make server` in the second terminal
before running `nettests` inside xv6.

## Quick test index

| Lab | Primary live command |
|---|---|
| Utilities | `primes` or `find . README` |
| System calls | `trace 32 grep hello README` |
| Page tables | boot output plus `usertests` |
| Traps | `alarmtest` |
| Lazy allocation | `lazytests` |
| Copy-on-write | `cowtest` |
| Multithreading | `uthread`; host-side `./ph 2` |
| Locks | `kalloctest`; `bcachetest` |
| File system | `bigfile`; `symlinktest` |
| mmap | `mmaptest` |
| Network driver | `nettests` |

