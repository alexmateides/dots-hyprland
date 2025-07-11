#!/bin/sh

print_lines() {
    printf '+\n-\n'
}
handle_choice() {
    case $1 in
    +) printf '\000message\037increase\n' ;;
    -) printf '\000message\037decrease\n' ;;
    esac
}

case $ROFI_RETV in
# print lines on start
0) print_lines ;;
# handle select line
1) handle_choice "$@" && print_lines ;;
esac