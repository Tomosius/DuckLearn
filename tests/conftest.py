# conftest.py
from __future__ import annotations

import collections
import os
import platform
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

import pytest
from rich import box
from rich.console import Console
from rich.table import Table
from rich.theme import Theme

# ---------- config ----------
STATUS_COLUMNS = ['passed', 'failed', 'error', 'skipped', 'xfail', 'xpass']
NUM_W = 5
SUBTOTAL_W = 8

COLOR = {
    'header': 'bold',
    'filepath': 'cyan',
    'func': 'bright_cyan',
    'passed': 'green',
    'failed': 'red',
    'error': 'red',
    'skipped': 'yellow',
    'xfail': 'yellow',
    'xpass': 'yellow',
    'subtotal': 'magenta',
    'total': 'bold',
}

# per-test records: (filepath, function, status)
_records: list[tuple[str, str, str]] = []


# ---------- helpers ----------
def _split_nodeid(nodeid: str) -> tuple[str, str]:
    parts = nodeid.split('::')
    filepath = parts[0]
    func = '.'.join(parts[1:]) if len(parts) > 1 else ''
    return filepath, func


def _status_from_report(report: pytest.TestReport) -> str:
    was_x = hasattr(report, 'wasxfail')
    if report.skipped and was_x:
        return 'xfail'
    if report.passed and was_x:
        return 'xpass'
    if report.outcome == 'passed':
        return 'passed'
    if report.outcome == 'failed':
        return 'failed' if report.when == 'call' else 'error'
    if report.outcome == 'skipped':
        return 'skipped'
    return report.outcome


def _shorten_middle(text: str, max_width: int) -> str:
    if max_width <= 0:
        return ''
    if len(text) <= max_width:
        return text
    if max_width <= 3:
        return '.' * max_width
    head = max_width // 2 - 1
    tail = max_width - head - 3
    return f'{text[:head]}...{text[-tail:]}'


def _allocate_widths(
    console: Console, include_function: bool
) -> tuple[int, int | None]:
    term_width = console.size.width
    numeric_total = NUM_W * len(STATUS_COLUMNS) + SUBTOTAL_W
    borders = 6 + 3 * (
        len(STATUS_COLUMNS) + (2 if include_function else 1) + 1
    )
    remaining = max(20, term_width - numeric_total - borders)
    if include_function:
        fp_w = max(18, int(remaining * 0.6))
        fn_w = max(14, remaining - fp_w)
        return fp_w, fn_w
    else:
        return max(20, remaining), None


def _header_labels(console: Console) -> dict[str, str]:
    compact = console.size.width < 100
    if compact:
        return {
            'passed': 'P',
            'failed': 'F',
            'error': 'E',
            'skipped': 'S',
            'xfail': 'XF',
            'xpass': 'XP',
        }
    return {c: c for c in STATUS_COLUMNS}


def _maybe_caption_for_labels(labels: dict[str, str]) -> str | None:
    if labels.get('passed') == 'P':
        return '[dim]P=passed  F=failed  E=error  S=skipped  XF=xfail  XP=xpass[/dim]'
    return None


def _guess_location(item) -> tuple[Path | None, int | None]:
    obj = getattr(item, 'obj', None)
    if obj is not None and hasattr(obj, '__code__'):
        try:
            p = Path(obj.__code__.co_filename)
            return p, obj.__code__.co_firstlineno
        except Exception:
            return None, None
    node = str(item.nodeid).split('::')[0]
    return Path(node), None


def _git(cmd: list[str]) -> str:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return out.stdout.strip()
    except Exception:
        return ''


def _git_info() -> dict[str, str]:
    commit = _git(['git', 'rev-parse', '--short', 'HEAD'])
    branch = _git(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    dirty = 'yes' if _git(['git', 'status', '--porcelain']) else 'no'
    return {'commit': commit, 'branch': branch, 'dirty': dirty}


# ---------- pytest options & config ----------
def pytest_addoption(parser: pytest.Parser) -> None:
    group = parser.getgroup('rich-table-report')
    group.addoption(
        '--test-report',
        choices=['summary', 'full'],
        default='summary',
        help="Colored table at end: 'summary' (per file) or 'full' (per test).",
    )
    group.addoption(
        '--term-width',
        type=int,
        default=None,
        help='Force terminal width (columns) for pytest/coverage output.',
    )
    group.addoption(
        '--repo-url-base',
        default='',
        help='Base URL for linking to source on the web, e.g. https://github.com/USER/REPO/blob/main',
    )
    group.addoption(
        '--open-html',
        action='store_true',
        default=False,
        help='Open the generated pytest-html report in the default browser on finish.',
    )


def pytest_configure(config: pytest.Config) -> None:
    # Clamp banner width (coverage/pytest often respect COLUMNS)
    tw = config.getoption('--term-width')
    if tw is None:
        try:
            tw = Console().size.width
        except Exception:
            tw = None
    if tw:
        os.environ['COLUMNS'] = str(tw)

    # ---- Environment metadata (for pytest-html + pytest-metadata) ----
    md = getattr(config, '_metadata', None)
    if md is None:
        try:
            config._metadata = {}
            md = config._metadata
        except Exception:
            md = {}
    gi = _git_info()
    md['Commit'] = gi['commit'] or 'N/A'
    md['Branch'] = gi['branch'] or 'N/A'
    md['Dirty'] = gi['dirty']
    md['Run at'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    md['Python'] = sys.version.split()[0]
    md['Platform'] = platform.platform()
    md['Executable'] = sys.executable


# ---------- collect results for Rich tables ----------
def pytest_runtest_logreport(report: pytest.TestReport) -> None:
    if report.when == 'call' or (
        report.failed and report.when in {'setup', 'teardown'}
    ):
        status = _status_from_report(report)
        fp, func = _split_nodeid(report.nodeid)
        _records.append((fp, func, status))


# ---------- Rich tables ----------
def _make_summary_table(console: Console) -> Table:
    fp_w, _ = _allocate_widths(console, include_function=False)
    labels = _header_labels(console)

    table = Table(
        title='Pytest Results (summary by file)',
        expand=False,
        box=box.SIMPLE_HEAVY,
        pad_edge=False,
    )
    table.add_column(
        'filepath',
        style=COLOR['filepath'],
        no_wrap=True,
        max_width=fp_w,
        overflow='ellipsis',
    )
    for col in STATUS_COLUMNS:
        table.add_column(
            labels[col],
            justify='right',
            width=NUM_W,
            no_wrap=True,
            header_style=COLOR[col],
            style=COLOR[col],
        )
    table.add_column(
        'SUBTOTAL',
        justify='right',
        width=SUBTOTAL_W,
        no_wrap=True,
        style=COLOR['subtotal'],
    )

    agg = collections.OrderedDict()
    for fp, _, status in _records:
        agg.setdefault(fp, collections.Counter())
        agg[fp][status] += 1

    totals = collections.Counter()
    for fp, cnt in agg.items():
        subtotal = sum(cnt.get(c, 0) for c in STATUS_COLUMNS)
        for c in STATUS_COLUMNS:
            totals[c] += cnt.get(c, 0)
        row = [
            f'[{COLOR["filepath"]}]{_shorten_middle(fp, fp_w)}[/{COLOR["filepath"]}]'
        ]
        row += [
            f'[{COLOR[c]}]{cnt.get(c, 0)}[/{COLOR[c]}]' for c in STATUS_COLUMNS
        ]
        row.append(f'[{COLOR["subtotal"]}]{subtotal}[/{COLOR["subtotal"]}]')
        table.add_row(*row)

    grand_total = sum(totals.get(c, 0) for c in STATUS_COLUMNS)
    total_row = ['[bold]TOTAL[/bold]']
    total_row += [
        f'[{COLOR[c]}]{totals.get(c, 0)}[/{COLOR[c]}]' for c in STATUS_COLUMNS
    ]
    total_row.append(
        f'[{COLOR["subtotal"]}]{grand_total}[/{COLOR["subtotal"]}]'
    )
    table.add_row(*total_row, style=COLOR['total'])

    cap = _maybe_caption_for_labels(labels)
    if cap:
        table.caption = cap
    return table


def _make_full_table(console: Console) -> Table:
    fp_w, fn_w = _allocate_widths(console, include_function=True)
    labels = _header_labels(console)

    table = Table(
        title='Pytest Results (full)',
        expand=False,
        box=box.SIMPLE_HEAVY,
        pad_edge=False,
    )
    table.add_column(
        'filepath',
        style=COLOR['filepath'],
        no_wrap=True,
        max_width=fp_w,
        overflow='ellipsis',
    )
    table.add_column(
        'function',
        style=COLOR['func'],
        no_wrap=True,
        max_width=fn_w,
        overflow='ellipsis',
    )
    for col in STATUS_COLUMNS:
        table.add_column(
            labels[col],
            justify='right',
            width=NUM_W,
            no_wrap=True,
            header_style=COLOR[col],
            style=COLOR[col],
        )
    table.add_column(
        'SUBTOTAL',
        justify='right',
        width=SUBTOTAL_W,
        no_wrap=True,
        style=COLOR['subtotal'],
    )

    totals = collections.Counter()
    for fp, func, status in _records:
        row = [
            f'[{COLOR["filepath"]}]{_shorten_middle(fp, fp_w)}[/{COLOR["filepath"]}]',
            f'[{COLOR["func"]}]{_shorten_middle(func, fn_w)}[/{COLOR["func"]}]',
        ]
        for col in STATUS_COLUMNS:
            val = 1 if status == col else 0
            totals[col] += val
            row.append(f'[{COLOR[col]}]{val}[/{COLOR[col]}]')
        row.append(f'[{COLOR["subtotal"]}]1[/{COLOR["subtotal"]}]')
        table.add_row(*row)

    grand_total = sum(totals.get(c, 0) for c in STATUS_COLUMNS)
    total_row = ['[bold]TOTAL[/bold]', '']
    total_row += [
        f'[{COLOR[c]}]{totals.get(c, 0)}[/{COLOR[c]}]' for c in STATUS_COLUMNS
    ]
    total_row.append(
        f'[{COLOR["subtotal"]}]{grand_total}[/{COLOR["subtotal"]}]'
    )
    table.add_row(*total_row, style=COLOR['total'])

    cap = _maybe_caption_for_labels(labels)
    if cap:
        table.caption = cap
    return table


def pytest_terminal_summary(
    terminalreporter, exitstatus: int, config: pytest.Config
) -> None:
    console = Console(theme=Theme({}))
    mode = config.getoption('--test-report')
    console.print()
    if not _records:
        console.print(
            '[dim]⚠️  No tests executed (nothing changed or nothing selected). '
            "Run 'pixi run test-html' or 'test-full' if needed.[/dim]"
        )
        console.print()
        return
    table = (
        _make_full_table(console)
        if mode == 'full'
        else _make_summary_table(console)
    )
    console.print(table)
    console.print()


# ---------- pytest-html hooks: tags, filters, links, metadata ----------
# HTML tag helpers
try:
    from py.xml import html as _HTML
except Exception:
    _HTML = None  # skip HTML customizations if unavailable


def pytest_html_report_title(report):
    report.title = 'Ducklearn – Test Report'


def pytest_html_results_summary(prefix, summary, postfix):
    # Quick anchors & filter tabs + inline CSS/JS
    if not _HTML:
        return

    # Filter "tabs"
    controls = _HTML.div(
        _HTML.span('Filter: ', style='margin-right:8px;'),
        _HTML.button('All', id='flt-all', **{'data-flt': 'all'}),
        _HTML.button('Failed', id='flt-failed', **{'data-flt': 'failed'}),
        _HTML.button('Passed', id='flt-passed', **{'data-flt': 'passed'}),
        _HTML.button('Skipped', id='flt-skipped', **{'data-flt': 'skipped'}),
        _HTML.button('XFail', id='flt-xfailed', **{'data-flt': 'xfailed'}),
        _HTML.button('XPass', id='flt-xpassed', **{'data-flt': 'xpassed'}),
        _HTML.button('Error', id='flt-error', **{'data-flt': 'error'}),
        id='filterbar',
        style='margin:8px 0 12px 0; display:flex; gap:8px; align-items:center; flex-wrap:wrap;',
    )

    style = _HTML.style("""
#filterbar button {
# padding:4px 10px; border:1px solid #aaa;
# background:#f5f5f5; border-radius:6px;
# cursor:pointer; }
#filterbar button.active { background:#ddd; font-weight:600; }
#results-table tr { transition: opacity .08s ease-in-out; }
    """)
    script = _HTML.script("""
(function(){
  function setActive(btn){
    document.querySelectorAll('#filterbar button').forEach(b=>b.classList.remove('active'));
    btn.classList.add('active');
  }
  function applyFilter(kind){
    const rows = document.querySelectorAll('#results-table tbody tr');
    rows.forEach(r=>{
      if(kind==='all'){ r.style.display=''; return; }
      const cls = r.getAttribute('class') || '';
      // pytest-html uses classes like: passed, failed, error, skipped, xfailed, xpassed
      if(cls.includes(kind)) r.style.display='';
      else r.style.display='none';
    });
  }
  document.addEventListener('DOMContentLoaded', function(){
    document.querySelectorAll('#filterbar button').forEach(btn=>{
      btn.addEventListener('click', function(){
        setActive(btn);
        applyFilter(btn.getAttribute('data-flt'));
      });
    });
    // default to "All"
    const all = document.getElementById('flt-all');
    if(all){ all.classList.add('active'); }
  });
})();
    """)

    prefix.extend(
        [
            _HTML.p(_HTML.a('Go to Failures', href='#results-table')),
            _HTML.p(_HTML.a('Go to Environment', href='#environment')),
            controls,
            style,
            script,
        ]
    )


def pytest_html_results_table_header(cells):
    if _HTML:
        cells.insert(0, _HTML.th('Path'))
        cells.insert(1, _HTML.th('Function'))


def pytest_html_results_table_row(report, cells):
    if not _HTML:
        return
    try:
        nodeid = report.nodeid
        fp, func = _split_nodeid(nodeid)
    except Exception:
        fp, func = ('', '')
    cells.insert(0, _HTML.td(fp))
    cells.insert(1, _HTML.td(func))


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Attach extras (links, captured io) for pytest-html."""
    outcome = yield
    report = outcome.get_result()

    if report.when != 'call':
        return

    try:
        from pytest_html import extras as _extras
    except Exception:
        _extras = None

    if _extras is None:
        return

    report.extra = getattr(report, 'extra', [])
    repo_base = item.config.getoption('--repo-url-base') or ''

    # Link to test source
    test_path, test_lineno = _guess_location(item)
    if test_path is not None:
        rel = Path(test_path).resolve().relative_to(Path.cwd())
        if repo_base:
            url = f'{repo_base}/{rel.as_posix()}' + (
                f'#L{test_lineno}' if test_lineno else ''
            )
            report.extra.append(_extras.url(url, name='View test source'))
        else:
            report.extra.append(
                _extras.text(f'Test: {rel}:{test_lineno or ""}')
            )

    # Best-effort implementation link: tests/test_foo.py -> src/foo.py
    impl_guess = None
    if test_path and 'tests' in test_path.parts:
        try:
            name = test_path.name
            if name.startswith('test_'):
                impl = name.replace('test_', '', 1)
                idx = test_path.parts.index('tests')
                impl_guess = Path(
                    *test_path.parts[:idx],
                    'src',
                    *test_path.parts[idx + 1 : -1],
                    impl,
                )
        except ValueError:
            pass
    if impl_guess and impl_guess.exists():
        rel_impl = impl_guess.resolve().relative_to(Path.cwd())
        if repo_base:
            report.extra.append(
                _extras.url(
                    f'{repo_base}/{rel_impl.as_posix()}',
                    name='View impl (guess)',
                )
            )
        else:
            report.extra.append(_extras.text(f'Impl (guess): {rel_impl}'))

    # Attach captured I/O if present
    if hasattr(report, 'capstdout') and report.capstdout:
        report.extra.append(_extras.text(report.capstdout, name='stdout'))
    if hasattr(report, 'capstderr') and report.capstderr:
        report.extra.append(_extras.text(report.capstderr, name='stderr'))


def pytest_sessionfinish(session: pytest.Session, exitstatus: int) -> None:
    """Auto-open HTML; also save history copy and build reports/index.html."""
    cfg = session.config
    htmlpath = getattr(cfg.option, 'htmlpath', None)  # set by --html
    if not htmlpath:
        return

    # ---- History & trends ----
    try:
        p = Path(htmlpath).resolve()
        reports_dir = p.parent
        hist_dir = reports_dir / 'history'
        hist_dir.mkdir(parents=True, exist_ok=True)

        gi = _git_info()
        stamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        tag = gi['commit'] or 'nocmt'
        dest = hist_dir / f'tests_{stamp}_{tag}.html'
        shutil.copyfile(p, dest)

        # Build (or update) a landing page with links to history + coverage
        cov_index = reports_dir / 'coverage' / 'index.html'
        items = sorted(
            hist_dir.glob('tests_*.html'),
            key=lambda q: q.stat().st_mtime,
            reverse=True,
        )

        rows = []
        for it in items:
            ts = datetime.fromtimestamp(it.stat().st_mtime).strftime(
                '%Y-%m-%d %H:%M:%S'
            )
            rows.append(
                f"<tr><td>{ts}</td><td><a href='history/{it.name}'>{it.name}</a></td></tr>"
            )

        index_html = f"""<!doctype html>
<html>
<head>
<meta charset="utf-8" />
<title>Ducklearn – Test Reports</title>
<style>
body{{font-family:system-ui,-apple-system,Segoe UI,Roboto,Ubuntu,Cantarell,sans-serif;margin:24px}}
h1{{margin-top:0}}
table{{border-collapse:collapse;width:100%}}
th,td{{border:1px solid #ddd;padding:8px}}
tr:nth-child(even){{background:#fafafa}}
a{{text-decoration:none}}
.btn{{display:inline-block;margin:6px 8px 12px 0;
padding:6px 10px;border:1px solid #aaa;border-radius:6px;background:#f5f5f5}}
</style>
</head>
<body>
<h1>Ducklearn – Test Reports</h1>
<p>
  <a class="btn" href="tests.html">Latest report</a>
  {"<a class='btn' href='coverage/index.html'>Coverage</a>" if cov_index.exists() else ''}
</p>
<h2>History</h2>
<table>
<thead><tr><th>Time</th><th>Report</th></tr></thead>
<tbody>
{''.join(rows)}
</tbody>
</table>
</body>
</html>"""
        (reports_dir / 'index.html').write_text(index_html, encoding='utf-8')
    except Exception:
        # Non-fatal: never break the test run if history generation fails
        pass

    # Auto-open current report if requested
    if cfg.getoption('--open-html'):
        try:
            import webbrowser

            webbrowser.open_new_tab(str(Path(htmlpath).resolve()))

        except Exception:
            pass
