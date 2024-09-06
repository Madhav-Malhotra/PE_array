module dump#(
    // Parameters for size of local register file
    parameter REG_SIZE = 4
)();
    initial begin
        // This syntax won't dump any array variables
        $dumpfile ("./test/pe.vcd");
        $dumpvars (0, pe);

        // So we manually dump array variables
        for (int i=0; i<REG_SIZE; i=i+1) begin
            $dumpvars (0, pe.regfile[i]);
        end
        #1;
    end
endmodule