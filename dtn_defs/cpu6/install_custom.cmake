message("inside install_custom cpu6")
target_include_directories(sch_lab.table INTERFACE
    $<TARGET_PROPERTY:cf,INCLUDE_DIRECTORIES>
    $<TARGET_PROPERTY:bpnode,INCLUDE_DIRECTORIES>
    $<TARGET_PROPERTY:bpacc_fun,INCLUDE_DIRECTORIES>
)
