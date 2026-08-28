`timescale 1ns/1ps

module uart_rx_fifo #(
    parameter CLK_FREQ = 50000000,
    parameter BAUD_RATE = 115200,
    parameter WIDTH = 8,
    parameter DEPTH = 16
)(
    input logic clk,
    input logic reset,

    input logic tx_write_en,
    input logic [WIDTH-1:0] tx_write_data,
    output logic tx_full,
    output logic tx_empty,

    input logic rx_read_en,
    output logic [WIDTH-1:0] rx_read_data,
    output logic rx_full,
    output logic rx_empty
);
    logic serial_wire;

    logic [WIDTH-1:0] rx_data_out;
    logic rx_data_valid;

    logic rx_fifo_write_en;

    uart_tx_fifo #(
        .CLK_FREQ(CLK_FREQ),
        .BAUD_RATE(BAUD_RATE),
        .WIDTH(WIDTH),
        .DEPTH(DEPTH)
    ) tx_module (
        .clk(clk),
        .reset(reset),

        .write_en(tx_write_en),
        .write_data(tx_write_data),

        .full(tx_full),
        .empty(tx_empty),
        .tx(serial_wire)
    );


    uart_rx #(
        .CLK_FREQ(CLK_FREQ),
        .BAUD_RATE(BAUD_RATE)
    ) rx_module(
        .clk(clk),
        .reset(reset),
        .rx(serial_wire),
        .data_out(rx_data_out),
        .data_valid(rx_data_valid)
    );

    assign rx_fifo_write_en = rx_data_valid && !rx_full;

    fifo #(
        .WIDTH(WIDTH),
        .DEPTH(DEPTH)
    ) rx_fifo (
        .clk(clk),
        .reset(reset),

        .write_en(rx_fifo_write_en),
        .write_data(rx_data_out),

        .read_en(rx_read_en),
        .read_data(rx_read_data),
        .full(rx_full),
        .empty(rx_empty)
    );
endmodule
