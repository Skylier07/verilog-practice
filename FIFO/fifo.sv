module fifo #(
    parameter WIDTH = 8,
    parameter DEPTH = 16,
)(
    input logic clk,
    input logic reset,
    input logic write_en,
    input logic [WIDTH-1:0] write_data,
    input logic read_en,
    output logic [WIDTH-1:0] read_data,

    output logic full,
    output logic empty,
);
    logic [$clog2(DEPTH)-1:0] write_ptr;
    logic [$clog2(DEPTH)-1:0] read_ptr;
    logic [WIDTH-1:0] mem [0:DEPTH-1];
    logic [$clog2(DEPTH)-1:0] count;
    

    always_ff @(posedge clk) begin
        if(reset) begin
            read_ptr <=0;
            write_ptr <=0;
            full <= 0;
            empty <=1;
            count <= 0;
        end
        if(write_en && !full) begin
            empty<=0;
            count<= count+1;

            mem[write_ptr] <= write_data;
            if(write_ptr>=(DEPTH-1)) begin
                write_ptr <= 0;
            end
            else
                write_ptr <= write_ptr+1'b1;
        end
        if(read_en && !empty) begin
            full <=0;
            read_data <= mem[read_ptr];
            read_ptr <= read_ptr + 1'b1;
            count<= count-1;
            if(read_ptr>=(DEPTH-1)) begin
                read_ptr_ptr <= 0;
            end
            else
                read_ptr <= read_ptr+1'b1;
        end
        if(count >= (DEPTH-1)) 
            full<=1;
        else if(count <= 0)
            empty<=1;
        else begin
            full<=0;
            empty<=0;
        end
    end

endmodule