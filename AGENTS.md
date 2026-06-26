# AGENTS.md

## Cursor Cloud specific instructions

This repository is a personal C++ practice project for *Introduction to Algorithms* (CLRS)
exercises. It is **not a service/application** — there are no servers, databases, ports, or
environment variables. Each `.cpp` file is a standalone console program with its own `main()`.

### Layout
- `Hello_world.cpp` — trivial sample program.
- `ch02/*.cpp` — Chapter 2 exercises (`E212`, `E213`, `E214`, `E222`, `Insertion_sort`, `Merge_sort`).
- Extension-less files (`hello_world`, `ch02/E212`, etc.) are pre-compiled binaries committed to git;
  prefer rebuilding from source rather than trusting them.

### Build & run
There is no build system (no Makefile/CMake) and no package manager. Compile and run files
individually with the preinstalled `g++` (13.x):

```bash
g++ ch02/Merge_sort.cpp -o /tmp/merge_sort && /tmp/merge_sort
```

To compile everything as a quick check:

```bash
for f in Hello_world.cpp ch02/*.cpp; do g++ "$f" -o "/tmp/$(basename "$f" .cpp).out"; done
```

### Notes / gotchas
- There are no automated tests and no lint configuration. "Testing" means compiling and running
  a program and inspecting its stdout.
- `ch02/Merge_sort.cpp` has a pre-existing logic bug (its sorted output is not fully sorted). This
  is a code issue in the exercise, not an environment problem — do not treat it as a setup failure.
