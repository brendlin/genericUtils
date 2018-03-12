################################################################################
# Package: genericUtils
################################################################################

# Declare the package name:
atlas_subdir( genericUtils )

# External dependencies:
find_package( ROOT COMPONENTS Core Hist PyROOT Graf Gpad )

# build a CINT dictionary for the library
atlas_add_root_dictionary ( genericUtilsLib genericUtilsCintDict
                            ROOT_HEADERS genericUtils/PlotFunctions.h
                            Root/LinkDef.h
                            EXTERNAL_PACKAGES ROOT
                            )

# build a shared library
atlas_add_library( genericUtilsLib
                   genericUtils/*.h genericUtils/*.cxx ${genericUtilsCintDict}
                   PUBLIC_HEADERS genericUtils
                   INCLUDE_DIRS ${ROOT_INCLUDE_DIRS}
                   LINK_LIBRARIES ${ROOT_LIBRARIES}
                   )
