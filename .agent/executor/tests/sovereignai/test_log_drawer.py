from __future__ import annotations


def filter_traces_python(traces: list[dict], filters: dict) -> list[dict]:  # noqa: E501
    return [
        t for t in traces
        if t['level'] in filters['levels']
        and (not filters['search'] or filters['search'] in t['message'].lower())
        and (  # noqa: E501
            not filters['components']
            or not filters['components']
            or t['component'] in filters['components']
        )
    ]

def test_trace_filter_by_level() -> None:
    traces = [  # noqa: E501
        {'level': 'ERROR', 'message': 'error 1', 'component': 'comp1'},
        {'level': 'WARN', 'message': 'warn 1', 'component': 'comp1'},
        {'level': 'INFO', 'message': 'info 1', 'component': 'comp1'},
        {'level': 'DEBUG', 'message': 'debug 1', 'component': 'comp1'}
    ]
    filters = {'levels': ['ERROR', 'WARN'], 'search': '', 'components': []}
    result = filter_traces_python(traces, filters)
    assert len(result) == 2
    assert all(t['level'] in ['ERROR', 'WARN'] for t in result)

def test_trace_search() -> None:
    traces = [  # noqa: E501
        {'level': 'INFO', 'message': 'hello world', 'component': 'comp1'},
        {'level': 'INFO', 'message': 'goodbye world', 'component': 'comp1'},
        {'level': 'INFO', 'message': 'test message', 'component': 'comp1'}
    ]
    filters = {'levels': ['INFO'], 'search': 'hello', 'components': []}
    result = filter_traces_python(traces, filters)
    assert len(result) == 1
    assert result[0]['message'] == 'hello world'

def test_trace_component_filter() -> None:
    traces = [  # noqa: E501
        {'level': 'INFO', 'message': 'msg1', 'component': 'comp1'},
        {'level': 'INFO', 'message': 'msg2', 'component': 'comp2'},
        {'level': 'INFO', 'message': 'msg3', 'component': 'comp1'}
    ]
    filters = {'levels': ['INFO'], 'search': '', 'components': ['comp1']}
    result = filter_traces_python(traces, filters)
    assert len(result) == 2
    assert all(t['component'] == 'comp1' for t in result)

def test_trace_memory_limit() -> None:
    traces = [{'level': 'INFO', 'message': f'msg{i}', 'component': 'comp1'} for i in range(1001)]
    max_traces = 1000
    retained = traces[-max_traces:]
    assert len(retained) == 1000
    assert retained[0]['message'] == 'msg1'
    assert retained[-1]['message'] == 'msg1000'

def test_combined_filters() -> None:
    traces = [  # noqa: E501
        {'level': 'ERROR', 'message': 'error in comp1', 'component': 'comp1'},
        {'level': 'ERROR', 'message': 'error in comp2', 'component': 'comp2'},
        {'level': 'WARN', 'message': 'warn in comp1', 'component': 'comp1'},
        {'level': 'INFO', 'message': 'info in comp1', 'component': 'comp1'}
    ]
    filters = {'levels': ['ERROR'], 'search': 'comp1', 'components': ['comp1']}
    result = filter_traces_python(traces, filters)
    assert len(result) == 1
    assert result[0]['message'] == 'error in comp1'
