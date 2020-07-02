export LD_LIBRARY_PATH="${APPDIR}/usr/lib:${LD_LIBRARY_PATH}"
export PATH="${APPDIR}/usr/bin:${PATH}"

{{ python-executable }} -s ${APPDIR}/usr/bin/saasbuild "$@"
