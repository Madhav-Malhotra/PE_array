module dump();
    initial begin
        $dumpfile ("./test/pe.vcd");
        $dumpvars (0, pe);
        #1;
    end
endmodule