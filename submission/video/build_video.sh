#!/bin/zsh
set -euo pipefail

video_dir="${0:A:h}"
repo_dir="${video_dir:h:h}"
export CLANG_MODULE_CACHE_PATH="/private/tmp/startone-video-clang-cache"
export SWIFT_MODULE_CACHE_PATH="/private/tmp/startone-video-swift-cache"

swiftc -parse-as-library "$video_dir/render_demo.swift" -o "$video_dir/build/render_demo"
"$video_dir/build/render_demo" "$repo_dir"
