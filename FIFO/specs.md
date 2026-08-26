# FIFO Project Specification

## Module

```systemverilog
module fifo #(
    parameter WIDTH = 8,
    parameter DEPTH = 16
)(
    input  logic             clk,
    input  logic             reset,

    input  logic             write_en,
    input  logic [WIDTH-1:0] write_data,

    input  logic             read_en,
    output logic [WIDTH-1:0] read_data,

    output logic             full,
    output logic             empty
);
```

## Parameters

* `WIDTH`: width of each FIFO entry in bits. Default: `8`.
* `DEPTH`: maximum number of entries. Default: `16`.

## Required Internal State

* Memory array containing `DEPTH` entries of `WIDTH` bits.
* Write pointer.
* Read pointer.
* Element count.
* Pointer width must support addresses `0` through `DEPTH - 1`.
* Count width must support values `0` through `DEPTH`.

## Reset

On synchronous reset:

* Read pointer = `0`.
* Write pointer = `0`.
* Element count = `0`.
* `empty = 1`.
* `full = 0`.
* Memory contents do not need to be cleared.

## Write

A write is accepted when:

```text
write_en && !full
```

On an accepted write:

* Store `write_data` at the current write pointer.
* Advance the write pointer.
* Wrap from `DEPTH - 1` to `0`.
* Increment count unless a read is also accepted.

Writes while `full` must be ignored.

## Read

A read is accepted when:

```text
read_en && !empty
```

The FIFO uses **registered-read semantics**.

On an accepted read:

* After the rising clock edge, `read_data` contains the entry at the previous read pointer.
* Advance the read pointer.
* Wrap from `DEPTH - 1` to `0`.
* Decrement count unless a write is also accepted.

Reads while `empty` must be ignored.

## Simultaneous Read/Write

If both operations are accepted on the same rising edge:

* Perform both operations.
* Advance both pointers.
* Leave count unchanged.

Boundary behavior:

* If full: accept the read, reject the write.
* If empty: accept the write, reject the read.

## Status Outputs

```text
empty = (count == 0)
full  = (count == DEPTH)
```

`full` and `empty` must never both be asserted.

## Ordering

The FIFO must preserve strict first-in, first-out ordering.

## Verification Requirements

The cocotb testbench must verify:

* Reset.
* Single write/read.
* Multiple writes/reads.
* FIFO ordering.
* Full and empty behavior.
* Rejected writes while full.
* Rejected reads while empty.
* Read/write pointer wraparound.
* Simultaneous read/write.
* Correct count behavior.
* Randomized operations using a Python queue as the reference model.
* Thousands of randomized cycles without loss, duplication, or reordering.
  ::: 
