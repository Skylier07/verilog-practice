`timescale 1ns/1ps
module fifo #(
    parameter WIDTH = 8,
    parameter DEPTH = 16
)(
    input logic clk,
    input logic reset,
    input logic write_en,
    input logic [WIDTH-1:0] write_data,
    input logic read_en,
    output logic [WIDTH-1:0] read_data,

    output logic full,
    output logic empty
);
    logic [$clog2(DEPTH)-1:0] write_ptr;
    logic [$clog2(DEPTH)-1:0] read_ptr;
    logic [WIDTH-1:0] mem [0:DEPTH-1];
    logic [$clog2(DEPTH):0] count;
    
    assign full = (count == DEPTH);
    assign empty = (count == 0);

    always_ff @(posedge clk) begin
        if(reset) begin
            read_ptr <=0;
            write_ptr <=0;
            count <= 0;
        end
        else begin
            if(write_en && !full) begin
                if(~read_en)
                    count<= count+1;
                else if(read_en && write_en)
                    count <= 0;
                mem[write_ptr] <= write_data;
                if(write_ptr>=(DEPTH)) begin
                    write_ptr <= 0;
                end
                else
                    write_ptr <= write_ptr+1'b1;
            end
            if(read_en && !empty) begin
                read_data <= mem[read_ptr];
                if(~write_en)
                    count<= count-1;
                if(read_ptr>=(DEPTH-1)) begin
                    read_ptr <= 0;
                end
                else
                    read_ptr <= read_ptr+1'b1;
            end
        end
    end

endmodule