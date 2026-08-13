# 8-bit ALU Mini-Project Specification

## Objective

Build a **combinational 8-bit ALU** in SystemVerilog.

The ALU takes two 8-bit inputs and an operation selector, performs one operation, and produces an 8-bit result plus four status flags.

This is the finished objective for this checkpoint.

---

## Module Interface

### Inputs

- `a[7:0]` — first 8-bit operand
- `b[7:0]` — second 8-bit operand
- `op[2:0]` — selects which operation the ALU performs

### Outputs

- `result[7:0]` — result of the selected operation
- `zero` — `1` when `result == 0`
- `negative` — equal to the most-significant bit of `result`
- `carry` — carry-out from addition
- `overflow` — signed overflow for addition or subtraction

There is **no clock** and **no reset**. This ALU is purely combinational.

---

## Operations

| `op` | Operation | Required behavior |
|---|---|---|
| `3'b000` | ADD | `result = a + b` |
| `3'b001` | SUB | `result = a - b` |
| `3'b010` | AND | `result = a & b` |
| `3'b011` | OR | <code>result = a &#124; b </code> |
| `3'b100` | XOR | `result = a ^ b` |
| `3'b101` | SHIFT LEFT | `result = a << 1` |
| `3'b110` | SHIFT RIGHT | `result = a >> 1` |
| `3'b111` | COMPARE | `result = 1` if unsigned `a < b`, otherwise `0` |

---

## Flag Rules

### `zero`

`zero = 1` whenever the final 8-bit `result` is all zeros.

### `negative`

`negative` is the most-significant bit of `result`.

For an 8-bit result, this is bit 7.

### `carry`

For **ADD**, `carry` is the ninth bit produced by the addition.

For every other operation in this project, set `carry = 0`.

### `overflow`

For **ADD** and **SUB**, `overflow` indicates signed two's-complement overflow.

For every other operation, set `overflow = 0`.

---

## Completion Criteria

The checkpoint is complete when:

1. All eight operations produce the required `result`.
2. `zero`, `negative`, `carry`, and `overflow` behave according to this specification.
3. The design is tested with a SystemVerilog testbench.
4. Normal cases and important edge cases pass.
5. A simple Python reference model can calculate expected ALU results and compare them against the RTL.

Do not add extra features yet.
