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

| Lab | Branch | Primary live command | Verified score |
|---|---|---|---:|
| Utilities | `sol-util` | `primes` or `find . README` | 100/100 |
| System calls | `sol-syscall` | `trace 32 grep hello README` | 35/35 |
| Page tables | `sol-pgtbl` | boot output plus `usertests` | 66/66 |
| Traps | `sol-traps` | `alarmtest` | 85/85 |
| Lazy allocation | `sol-lazy` | `lazytests` | 119/119 |
| Copy-on-write | `sol-cow` | `cowtest` | 110/110 |
| Multithreading | `sol-thread` | `uthread`; host-side `./ph 2` | 60/60 |
| Locks | `sol-lock` | `kalloctest`; `bcachetest` | 70/70 |
| File system | `sol-fs` | `bigfile`; `symlinktest` | 100/100 |
| mmap | `sol-mmap` | `mmaptest` | 140/140 |
| Network driver | `sol-net` | `nettests` | 100/100 |

## High-value oral questions

1. Why must `copyout` explicitly resolve both lazy pages and COW pages?
2. Which PTE flag distinguishes an original read-only page from a COW page?
3. Why must a per-process kernel page table also map the process kernel stack?
4. Why is a generation counter required for a reusable condition-variable barrier?
5. How does `evict_lock` preserve one cached `buf` per disk block without
   putting cache hits back under a global lock?
6. Why may `e1000_recv` not call `net_rx` while holding `e1000_lock`?
7. What must be freed by `itrunc` for a doubly-indirect file?
8. When does `MAP_SHARED` write data back, and why does `MAP_PRIVATE` not do so?
