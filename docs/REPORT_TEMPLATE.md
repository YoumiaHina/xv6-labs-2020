# xv6 Labs experiment report

## Project overview

- Course version: MIT 6.S081 Fall 2020
- Architecture: RISC-V
- Runtime: xv6 under QEMU
- Repository: <https://github.com/YoumiaHina/xv6-labs-2020>

## Environment and verification

Document the WSL2, Ubuntu, compiler, QEMU, and GDB versions. Explain the three
Ubuntu 24.04 compatibility adjustments separately from the lab solutions.

## Per-lab section template

Use this structure once for each of the eleven labs.

### Objective

State the operating-system mechanism exercised by the lab.

### Design

Describe the data flow, modified invariants, concurrency rules, and error
handling. Include a small diagram only when it makes the mechanism clearer.

### Key implementation

Show only the relevant snippets and explain why each change is required. Link
to the exact solution branch instead of pasting the full source.

### Tests and results

List the exact commands, important observable output, and final `make grade`
result. Use at most two screenshots per lab.

### Problems and analysis

Record at least one debugging observation, its root cause, and the final fix.

## Overall conclusions

Summarize how system calls, virtual memory, traps, concurrency, the file
system, memory mapping, and device drivers fit together in xv6.

