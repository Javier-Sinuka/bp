#
# arch_build_custom_microblazeel.cmake
# ------------------------------------
#
add_compile_options(
    -Wcast-align=strict         # Warn about casts that increase alignment requirements
    -fno-common                 # Do not use a common section for globals
)
