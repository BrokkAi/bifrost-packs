import java.util.Map;
import java.util.HashMap;
import java.util.function.BiConsumer;

/** Authored analyzer fixtures; methods are not runtime performance benchmarks. */
final class MapKeySetLookupCases {
  int positiveSameMapAndKey(Map<String, Integer> map) {
    int total = 0;
    for (String key : map.keySet()) {
      Integer value = map.get(key);
      if (value != null) total += value;
    }
    return total;
  }

  int nearKeyOnly(Map<String, Integer> map) {
    int total = 0;
    for (String key : map.keySet()) total += key.length();
    return total;
  }

  int nearEntrySet(Map<String, Integer> map) {
    int total = 0;
    for (Map.Entry<String, Integer> entry : map.entrySet()) {
      Integer value = entry.getValue();
      if (value != null) total += value;
    }
    return total;
  }

  int nearDifferentMap(Map<String, Integer> map, Map<String, Integer> other) {
    int total = 0;
    for (String key : map.keySet()) {
      Integer value = other.get(key);
      if (value != null) total += value;
    }
    return total;
  }

  int nearGetOutsideLoop(Map<String, Integer> map) {
    int total = 0;
    for (String key : map.keySet()) total += key.length();
    Integer value = map.get("outside");
    if (value != null) total += value;
    return total;
  }

  int nearNestedDifferentKey(Map<String, Integer> map,
                             java.util.Set<String> candidates) {
    int total = 0;
    for (String key : map.keySet()) {
      for (String candidate : candidates) {
        Integer value = map.get(candidate);
        if (value != null) total += value;
      }
    }
    return total;
  }

  int nearChangedKey(Map<String, Integer> map) {
    int total = 0;
    for (String key : map.keySet()) {
      key = key.trim();
      Integer value = map.get(key);
      if (value != null) total += value;
    }
    return total;
  }

  int nearMutationBeforeLookup(Map<String, Integer> map) {
    int total = 0;
    for (String key : map.keySet()) {
      map.remove(key);
      Integer value = map.get(key);
      if (value != null) total += value;
    }
    return total;
  }

  int incompleteUnknownEffect(Map<String, Integer> map,
                              BiConsumer<Map<String, Integer>, String> callback) {
    int total = 0;
    for (String key : map.keySet()) {
      callback.accept(map, key);
      Integer value = map.get(key);
      if (value != null) total += value;
    }
    return total;
  }

  int nearReassignedMap(Map<String, Integer> map,
                        Map<String, Integer> other) {
    int total = 0;
    Map<String, Integer> selected = map;
    for (String key : map.keySet()) {
      selected = other;
      Integer value = selected.get(key);
      if (value != null) total += value;
    }
    return total;
  }

  int candidateAliasedMap(Map<String, Integer> map) {
    int total = 0;
    Map<String, Integer> alias = map;
    for (String key : alias.keySet()) {
      Integer value = map.get(key);
      if (value != null) total += value;
    }
    return total;
  }

  int nearCustomMapContract(RecordingMap map) {
    int total = 0;
    for (String key : map.keySet()) {
      Integer value = map.get(key);
      if (value != null) total += value;
    }
    return total;
  }

  int nearLocalLookalike(LocalMap map) {
    int total = 0;
    for (String key : map.keySet()) {
      Integer value = map.get(key);
      if (value != null) total += value;
    }
    return total;
  }

  static final class RecordingMap extends HashMap<String, Integer> {
    int reads;

    @Override
    public Integer get(Object key) {
      reads++;
      return super.get(key);
    }
  }

  static final class LocalMap {
    java.util.Set<String> keySet() { return java.util.Collections.emptySet(); }
    Integer get(String key) { return 1; }
  }
}
