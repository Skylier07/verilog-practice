# UART RX FIFO Integration Specification

## 1. Goal

Extend the existing verified UART system by adding an RX FIFO after `uart_rx`.

Previous system:

```text
TX FIFO
   ↓
UART TX
   ↓
serial wire
   ↓
UART RX
   ↓
Python / cocotb
```

New system:

```text
TX FIFO
   ↓
UART TX
   ↓
serial wire
   ↓
UART RX
   ↓
RX FIFO
   ↓
Python / cocotb
```

The RX FIFO stores successfully received UART bytes until the consumer is ready to read them.

---

## 2. Files

Keep the existing modules separate:

```text
fifo.sv
uart_tx.sv
uart_rx.sv
uart_tx_fifo.sv
```

Create a new top-level file:

```text
uart_rx_fifo.sv
```

`uart_rx_fifo.sv` should instantiate:

- one TX FIFO
- one UART TX
- one UART RX
- one RX FIFO

Do not copy the implementations of `fifo`, `uart_tx`, or `uart_rx` into this file.

---

## 3. Top-Level Module

Use a top-level module approximately like:

```systemverilog
module uart_rx_fifo #(
    parameter CLK_FREQ  = 50_000_000,
    parameter BAUD_RATE = 115200,
    parameter FIFO_DEPTH = 16
)(
    input  logic       clk,
    input  logic       reset,

    // TX FIFO write interface
    input  logic       tx_write_en,
    input  logic [7:0] tx_write_data,
    output logic       tx_full,
    output logic       tx_empty,

    // RX FIFO read interface
    input  logic       rx_read_en,
    output logic [7:0] rx_read_data,
    output logic       rx_full,
    output logic       rx_empty
);
```

Exact signal names may differ, but the interface should clearly distinguish the TX FIFO side from the RX FIFO side.

---

## 4. Internal Architecture

The data path must be:

```text
tx_write_data
      │
      ▼
┌───────────┐
│  TX FIFO  │
└─────┬─────┘
      │
      ▼
┌───────────┐
│  UART TX  │
└─────┬─────┘
      │ tx
      ▼
   serial
      │
      ▼
┌───────────┐
│  UART RX  │
└─────┬─────┘
      │
      │ rx_data_out
      │ rx_data_valid
      ▼
┌───────────┐
│  RX FIFO  │
└─────┬─────┘
      │
      ▼
 rx_read_data
```

The TX side should retain the already-working Part 5 behavior.

Do not redesign the TX path unless a bug is discovered.

---

## 5. UART RX → RX FIFO Interface

The UART RX produces:

```systemverilog
rx_data_out
rx_data_valid
```

Where:

- `rx_data_out` is the newly received byte.
- `rx_data_valid` is asserted for exactly one clock cycle when a complete valid UART byte has been received.

The RX FIFO consumes:

```systemverilog
write_en
write_data
```

Connect the data path conceptually as:

```text
UART RX rx_data_out
        ↓
RX FIFO write_data
```

The RX FIFO should attempt a write whenever a new UART byte arrives.

---

## 6. RX FIFO Write Condition

A received byte may only be written if the RX FIFO has space.

Required behavior:

```text
rx_data_valid = 1
rx_full       = 0
        ↓
write received byte into RX FIFO
```

If:

```text
rx_data_valid = 1
rx_full       = 1
```

then:

```text
drop the newly received byte
```

For this version, no retry mechanism is required.

Conceptually:

```systemverilog
rx_fifo_write_en = rx_data_valid && !rx_full;
```

The exact implementation is up to you.

---

## 7. RX FIFO Write Data

Whenever a byte is accepted into the RX FIFO:

```text
RX FIFO write_data = UART RX data_out
```

The byte must not be modified, reversed, incremented, or otherwise transformed.

Example:

```text
UART RX receives 0xA7
        ↓
RX FIFO stores 0xA7
```

---

## 8. RX FIFO Read Interface

The testbench acts as the consumer of the RX FIFO.

It controls:

```systemverilog
rx_read_en
```

and observes:

```systemverilog
rx_read_data
rx_empty
rx_full
```

The RX FIFO must preserve the same read semantics as the standalone FIFO built earlier.

Do not create a second, different FIFO implementation.

---

## 9. FIFO Ordering Requirement

The RX FIFO must preserve byte order.

If UART RX receives:

```text
0x12
0x34
0x56
0x78
```

then the consumer must read:

```text
0x12
0x34
0x56
0x78
```

in exactly that order.

This is FIFO behavior:

```text
First In → First Out
```

---

## 10. Empty Behavior

After reset:

```text
rx_empty = 1
```

After the first received byte is successfully written:

```text
rx_empty = 0
```

After all stored bytes have been successfully read:

```text
rx_empty = 1
```

The testbench must not treat `rx_read_data` as a valid new byte when the FIFO is empty.

---

## 11. Full Behavior

When the RX FIFO reaches its configured capacity:

```text
rx_full = 1
```

Existing stored bytes must remain unchanged.

If another UART byte arrives while full:

```text
new byte is dropped
```

The FIFO must not overwrite unread data.

For Part 6, an overflow/error output is not required.

---

## 12. Reset Behavior

When `reset` is asserted:

- TX FIFO becomes empty.
- RX FIFO becomes empty.
- UART TX returns to idle.
- UART RX returns to idle/waiting-for-start state.
- No stale byte should remain logically available from either FIFO.

After reset:

```text
tx_empty = 1
rx_empty = 1
```

Normal communication should work again without requiring another reset.

---

# Verification Requirements

## Test 1 — Single Byte

Write:

```text
0xA7
```

into the TX FIFO.

Allow it to travel through:

```text
TX FIFO
→ UART TX
→ UART RX
→ RX FIFO
```

Verify:

```text
rx_empty == 0
```

Read one byte from RX FIFO.

Expected:

```text
0xA7
```

Then verify:

```text
rx_empty == 1
```

---

## Test 2 — Four Known Bytes

Write quickly into the TX FIFO:

```text
0x12
0x34
0x56
0x78
```

Do not read the RX FIFO while the bytes are being transmitted.

After all four bytes have arrived, read four times.

Expected sequence:

```text
0x12
0x34
0x56
0x78
```

After the final read:

```text
rx_empty == 1
```

---

## Test 3 — Recognizable Byte Patterns

Test sequences containing:

```text
0x00
0xFF
0x55
0xAA
0x01
0x80
0xA7
```

Verify that every received byte matches the transmitted byte exactly.

---

## Test 4 — RX FIFO Accumulation

Do not immediately read received bytes.

Allow several bytes to accumulate inside the RX FIFO.

Conceptually verify occupancy behavior:

```text
0 → 1 → 2 → 3 → ...
```

Then drain the FIFO.

The bytes must remain in correct order.

---

## Test 5 — RX FIFO Full

Use a small FIFO depth if helpful for simulation.

For example:

```text
FIFO_DEPTH = 4
```

Allow four bytes to arrive without reading.

Verify:

```text
rx_full == 1
```

Then allow another UART byte to arrive.

Expected:

- FIFO remains valid.
- Previously stored bytes remain unchanged.
- The extra byte is dropped.
- No unread byte is overwritten.

---

## Test 6 — Drain After Full

After filling the RX FIFO, begin reading bytes.

Verify that:

```text
rx_full
```

deasserts after enough space becomes available.

Continue reading until:

```text
rx_empty == 1
```

---

## Test 7 — Refill After Drain

After completely draining the RX FIFO, send more bytes.

Verify that the FIFO can accept and return new traffic normally.

This helps catch pointer-wrap and stale-state bugs.

---

# Part 6 Completion Criteria

Part 6 is complete when all of the following are true:

- [ ] Existing TX FIFO path still works.
- [ ] UART RX still correctly receives transmitted bytes.
- [ ] Every valid UART byte is written into RX FIFO when space exists.
- [ ] RX FIFO preserves byte ordering.
- [ ] RX FIFO can hold multiple received bytes before Python reads them.
- [ ] `rx_empty` behaves correctly.
- [ ] `rx_full` behaves correctly.
- [ ] RX FIFO does not overwrite unread data.
- [ ] Bytes arriving while RX FIFO is full are dropped.
- [ ] RX FIFO works again after being drained.
- [ ] Reset empties both FIFOs.
- [ ] Cocotb can send bytes through the entire chain and later read the same bytes from RX FIFO.

---

# Scope Restrictions

Do **not** add yet:

- parity
- multiple stop-bit modes
- configurable UART word length
- RTS/CTS flow control
- RX overflow interrupt
- framing-error output
- 16× UART oversampling
- a new FIFO implementation
- additional RX controller FSMs unless truly necessary

The goal of Part 6 is only:

```text
verified TX FIFO
      ↓
verified UART TX
      ↓
verified UART RX
      ↓
verified RX FIFO integration
```

Once this works reliably, proceed to full-system randomized verification.
