
message("inside install_custom cpu2")
target_include_directories(sch_lab.table INTERFACE
    $<TARGET_PROPERTY:cf,INCLUDE_DIRECTORIES>
    $<TARGET_PROPERTY:bpnode,INCLUDE_DIRECTORIES>
)
