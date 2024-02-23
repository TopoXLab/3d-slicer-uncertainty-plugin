cmake_minimum_required(VERSION 3.16.3...3.19.7 FATAL_ERROR)

project(UncertaintyRemoverExtension)

#-----------------------------------------------------------------------------
# Extension meta-information
set(EXTENSION_HOMEPAGE "https://www.slicer.org/wiki/Documentation/Nightly/Extensions/UncertaintyRemover")
set(EXTENSION_CATEGORY "Examples")
set(EXTENSION_CONTRIBUTORS "Sumedh Ghavat (Stony Brook University)")
set(EXTENSION_DESCRIPTION "This extension is developed as part of uncertainty remover tool")
set(EXTENSION_ICONURL "https://www.example.com/Slicer/Extensions/UncertaintyRemover.png")
set(EXTENSION_SCREENSHOTURLS "https://www.example.com/Slicer/Extensions/UncertaintyRemover/Screenshots/1.png")
set(EXTENSION_DEPENDS "NA") # Specified as a list or "NA" if no dependencies

#-----------------------------------------------------------------------------
# Extension dependencies
find_package(Slicer REQUIRED)
include(${Slicer_USE_FILE})

#-----------------------------------------------------------------------------
# Extension modules
add_subdirectory(UncertaintyRemoverModule)
add_subdirectory(Example)
add_subdirectory(Uncertainty)
add_subdirectory(New)
add_subdirectory(Uncertainty)
add_subdirectory(new1)
## NEXT_MODULE

#-----------------------------------------------------------------------------
include(${Slicer_EXTENSION_GENERATE_CONFIG})
include(${Slicer_EXTENSION_CPACK})
