#!/usr/bin/env bash
# Run the Bruin pipeline with UV_TOOL_DIR set to a project-local directory
# and --workers 1 so only one asset uses DuckDB at a time (avoids "file in use").
# See: https://docs.astral.sh/uv/reference/environment/
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
export UV_TOOL_DIR="${SCRIPT_DIR}/.uv-tools"
mkdir -p "$UV_TOOL_DIR"

# On Windows, PyArrow/ingestr need a timezone database (avoid "Timezone database not found").
if [[ "$OSTYPE" == msys ]] || [[ "$OSTYPE" == cygwin ]] || [[ -n "$WINDIR" ]]; then
  TZDIR_DEFAULT="${USERPROFILE:-$HOME}/Downloads/tzdata"
  mkdir -p "$TZDIR_DEFAULT" 2>/dev/null
  python -c "
import sys
try:
  import pyarrow as pa
  if hasattr(pa.util, 'download_tzdata_on_windows'):
    pa.util.download_tzdata_on_windows()
except Exception:
  pass
" 2>/dev/null
  export TZDIR="${TZDIR:-$TZDIR_DEFAULT}"
fi

exec bruin run ./pipeline/pipeline.yml --workers 1 "$@"
