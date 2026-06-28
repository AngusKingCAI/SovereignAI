// SovereignAI web UI - testable pure functions

function filterTraces(traces, filters) {
  return traces.filter(t => {
    if (!filters.levels.includes(t.level)) return false;
    if (filters.search && !t.message.toLowerCase().includes(filters.search)) return false;
    if (filters.components && filters.components.length && !filters.components.includes(t.component)) return false;
    return true;
  });
}
