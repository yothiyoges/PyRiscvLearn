# Copyright 2018 SiFive, Inc
# SPDX-License-Identifier: Apache-2.0

# The name, version, and maintainer of this package
AC_INIT([elf2hex], [m4_esyscmd_s([./scripts/git-version])], [palmer@sifive.com])

AC_CANONICAL_TARGET

AM_INIT_AUTOMAKE([foreign subdir-objects])
AM_MAINTAINER_MODE([disable])

AM_PATH_PYTHON([3.5])
AC_PATH_TARGET_TOOL(OBJCOPY, objcopy)
AC_SUBST(PYTHON)
AC_SUBST(pythondir)

# Generates the remainder of the build system.
AC_CONFIG_FILES([Makefile])
AC_OUTPUT
