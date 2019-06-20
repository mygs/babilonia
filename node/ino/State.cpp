#include <State.h>

const char* diffs(JsonVariant _base, JsonVariant _arrived) {
  const char *arrived = _arrived.as<char *>();
  if ((arrived != NULL) && (arrived[0] != '\0')) {
    return arrived;
  } else {
    return _base.as<char *>();
  }
}

int diffi(JsonVariant _base, JsonVariant _arrived) {
  int arrived = _arrived.as<int>();
  if (arrived >= 0) {
    return arrived;
  } else {
    return _base.as<int>();
  }
}

bool diffb(JsonVariant _base, JsonVariant _arrived) {
  if (!_arrived.isNull()) {
    return _arrived.as<bool>();
  } else {
    return _base.as<bool>();
  }
}
