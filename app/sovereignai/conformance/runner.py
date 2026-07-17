import collections

from app.sovereignai.conformance.registry import get_conformance_tests_for_class
from app.sovereignai.shared.trace_emitter import TraceEmitter
from app.sovereignai.shared.types import TraceLevel


class ConformanceRunner:

    def __init__(self, trace: TraceEmitter) -> None:
        self._trace = trace
        self._cache: collections.OrderedDict[tuple[str, str], bool] = collections.OrderedDict()

    def _cache_set(self, key: tuple[str, str], value: bool) -> None:
        self._cache[key] = value
        self._cache.move_to_end(key)
        if len(self._cache) > 1024:
            self._cache.popitem(last=False)

    def check(
        self,
        component_id: str,
        content_hash: str,
        capability_class: str,
        instance: object,
        is_first_party: bool = False,
    ) -> bool:
        cache_key = (component_id, content_hash)
        if cache_key in self._cache:
            self._cache.move_to_end(cache_key)  # F9: LRU — mark as recently used
            return self._cache[cache_key]

        test_classes = get_conformance_tests_for_class(capability_class)
        if not test_classes:
            if is_first_party:
                # F2: fail-CLOSED for first-party — missing tests is a STOP condition
                self._trace.emit(
                    component="conformance",
                    level=TraceLevel.ERROR,
                    message=(
                        f"First-party component {component_id} has NO "
                        f"conformance tests for capability class "
                        f"'{capability_class}' — registration blocked "
                        f"(fail-closed per F2)"
                    ),
                )
                self._cache[cache_key] = False
                if len(self._cache) > 1024:
                    self._cache.popitem(last=False)  # F9: LRU eviction
                return False
            else:
                # F2: fail-OPEN for third-party — missing tests is a WARN
                self._trace.emit(
                    component="conformance",
                    level=TraceLevel.WARN,
                    message=(
                        f"Third-party component {component_id} has no "
                        f"conformance tests for capability class "
                        f"'{capability_class}'; allowing registration "
                        f"(fail-open per F2)"
                    ),
                )
                self._cache[cache_key] = True
                if len(self._cache) > 1024:
                    self._cache.popitem(last=False)  # F9: LRU eviction
                return True

        for test_class in test_classes:
            test_instance = test_class()
            try:
                for method_name in dir(test_instance):
                    if method_name.startswith("test_"):
                        getattr(test_instance, method_name)(instance)
            except AssertionError as e:
                self._trace.emit(
                    component="conformance",
                    level=TraceLevel.ERROR,
                    message=(
                        f"Conformance test {test_class.__name__}."
                        f"{method_name} failed for {component_id}: {e}"
                    ),
                )
                self._cache[cache_key] = False
                return False
            except Exception as e:
                self._trace.emit(
                    component="conformance",
                    level=TraceLevel.ERROR,
                    message=(
                        f"Conformance test {test_class.__name__}."
                        f"{method_name} raised for {component_id}: {e}"
                    ),
                )
                self._cache[cache_key] = False
                return False

        self._cache[cache_key] = True
        return True
