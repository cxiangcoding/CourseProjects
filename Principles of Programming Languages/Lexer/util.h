bool ispdigit8(char ch) {
    return (ch >= '1' && ch <= '7');
}

bool isdigit8(char ch) {
    return (ch >= '0' && ch <= '7');
}

bool ispdigit16(char ch) {
    return ((ch >= '1' && ch <= '9') || (ch >= 'A' && ch <= 'F') || (ch >= 'a' && ch <= 'f'));
}

bool isdigit16(char ch) {
    return ((ch >= '0' && ch <= '9') || (ch >= 'A' && ch <= 'F') || (ch >= 'a' && ch <= 'f'));
}

bool ispdigit(char ch) {
    return (ch >= '1' && ch <= '9');
}