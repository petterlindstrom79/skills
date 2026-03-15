#!/bin/bash
# HashGen - File and text hash generator
cmd_text() { local algo="${1:-sha256}"; shift; local text="$*"
    [ -z "$text" ] && { echo "Usage: hashgen text [algo] <text>"; echo "Algos: md5, sha1, sha256, sha512"; return 1; }
    echo -n "$text" | "${algo}sum" 2>/dev/null | awk '{print $1}' || python3 -c "import hashlib; print(hashlib.new('$algo','$text'.encode()).hexdigest())"
}
cmd_file() { local algo="${1:-sha256}"; local file="$2"
    [ -z "$file" ] && { echo "Usage: hashgen file [algo] <file>"; return 1; }
    [ ! -f "$file" ] && { echo "File not found: $file"; return 1; }
    "${algo}sum" "$file" 2>/dev/null || python3 -c "
import hashlib
h=hashlib.new('$algo')
with open('$file','rb') as f:
 for chunk in iter(lambda:f.read(8192),b''): h.update(chunk)
print('{}  {}'.format(h.hexdigest(),'$file'))
"
}
cmd_verify() { local file="$1" expected="$2" algo="${3:-sha256}"
    [ -z "$file" ] || [ -z "$expected" ] && { echo "Usage: hashgen verify <file> <expected_hash> [algo]"; return 1; }
    local actual=$(cmd_file "$algo" "$file" | awk '{print $1}')
    if [ "$actual" = "$expected" ]; then echo "✅ Match! File integrity verified."
    else echo "❌ Mismatch!"; echo "  Expected: $expected"; echo "  Got:      $actual"; fi
}
cmd_compare() { local f1="$1" f2="$2" algo="${3:-sha256}"
    [ -z "$f1" ] || [ -z "$f2" ] && { echo "Usage: hashgen compare <file1> <file2> [algo]"; return 1; }
    local h1=$(cmd_file "$algo" "$f1" | awk '{print $1}')
    local h2=$(cmd_file "$algo" "$f2" | awk '{print $1}')
    if [ "$h1" = "$h2" ]; then echo "✅ Files are identical ($algo)"
    else echo "❌ Files differ"; echo "  $f1: $h1"; echo "  $f2: $h2"; fi
}
cmd_all() { local text="$*"
    [ -z "$text" ] && { echo "Usage: hashgen all <text>"; return 1; }
    echo "All hashes for: $text"
    for algo in md5 sha1 sha256 sha512; do
        hash=$(echo -n "$text" | "${algo}sum" 2>/dev/null | awk '{print $1}' || python3 -c "import hashlib; print(hashlib.new('$algo','$text'.encode()).hexdigest())")
        printf "  %-8s %s\n" "$algo" "$hash"
    done
}
cmd_help() { echo "HashGen - Hash Generator & Verifier"; echo "Commands: text [algo] <text> | file [algo] <file> | verify <file> <hash> [algo] | compare <f1> <f2> | all <text> | help"; echo "Algos: md5, sha1, sha256 (default), sha512"; }
cmd_info() { echo "HashGen v1.0.0 | Powered by BytesAgain"; }
case "$1" in text) shift; cmd_text "$@";; file) shift; cmd_file "$@";; verify) shift; cmd_verify "$@";; compare) shift; cmd_compare "$@";; all) shift; cmd_all "$@";; info) cmd_info;; help|"") cmd_help;; *) cmd_help; exit 1;; esac
