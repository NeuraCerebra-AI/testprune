# Final response format

The last message of a testprune run must be readable by someone who did not watch the work and must never leave them asking "so are we finished?". Structure it exactly like this, in this order, under about 350 words of prose.

1. **Outcome in one sentence.** "Finished and committed" or "Finished, not committed" or "Stopped at the time budget; here is what landed."
2. **Visualization 1: wall time before and after** (template below).
3. **Three piles, labeled:**
   - **Done** (nothing to do): what changed, in plain words. One short metaphor is fine (a garage, a toolbox), no jargon without a gloss.
   - **Optional** (housekeeping, no effect on speed): things that would be nice but are not required. Say explicitly that they do not slow anything down, if that is true.
   - **Parked** (skipped on purpose): each item with the one-line reason and where it is recorded.
4. **Visualization 2: what the runner collects versus what git tracks** (template below).
5. **Numbers table**: fast gate, subsystem gate, broad gate, slowest tests before and after, failures before and after. Only measured values.
6. **Files changed** as a short list; **not pushed / not committed** stated plainly.

Rules: numbers come from tool output; every displayed number is rounded (integers for counts, one decimal for minutes); widgets carry only the visual, all explanation stays in the response text; no arrows or em-dashes in prose; do not re-list optional items as if they were open work; if the visualize tool is unavailable, replace each visualization with a markdown table carrying the same numbers.

## Visualizations

Use the `visualize` MCP tools when available. Call `read_me` with modules `["chart", "diagram"]` first (silently, do not narrate it), then `show_widget` once per visual. Put explanatory prose in the response, not inside the widget. Fill every `{{placeholder}}` with measured values; delete a metric card rather than invent a number.

### Visualization 1: wall time before and after (HTML, Chart.js)

Loading messages: two playful ones, e.g. `["Timing the test suite's diet", "Shrinking minutes into seconds"]`. Title: `test_run_wall_time_before_after_audit`.

```html
<h2 class="sr-only" style="position:absolute;width:1px;height:1px;overflow:hidden;clip:rect(0 0 0 0);">Test run wall time before and after: a quick check drops from {{BEFORE_MIN}} minutes to {{FAST_LABEL}}, a subsystem run to {{SUBSYSTEM_LABEL}}, and the whole suite to {{BROAD_LABEL}}; failures to read drop from {{FAILS_BEFORE}} to {{FAILS_AFTER}}.</h2>
<div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin:0 0 1.5rem;">
  <div style="background:var(--surface-1);border-radius:var(--radius);padding:1rem;">
    <div style="font-size:13px;color:var(--text-secondary);margin-bottom:4px;">Quick check after an edit</div>
    <div style="font-size:24px;font-weight:500;color:var(--text-primary);">{{FAST_LABEL}}</div>
    <div style="font-size:13px;color:var(--text-muted);">was {{BEFORE_LABEL}}</div>
  </div>
  <div style="background:var(--surface-1);border-radius:var(--radius);padding:1rem;">
    <div style="font-size:13px;color:var(--text-secondary);margin-bottom:4px;">Failures an agent must read</div>
    <div style="font-size:24px;font-weight:500;color:var(--text-primary);">{{FAILS_AFTER}}</div>
    <div style="font-size:13px;color:var(--text-muted);">was {{FAILS_BEFORE}}, all now classified</div>
  </div>
  <div style="background:var(--surface-1);border-radius:var(--radius);padding:1rem;">
    <div style="font-size:13px;color:var(--text-secondary);margin-bottom:4px;">Slowest tests fixed</div>
    <div style="font-size:24px;font-weight:500;color:var(--text-primary);">{{SLOW_AFTER_LABEL}}</div>
    <div style="font-size:13px;color:var(--text-muted);">was {{SLOW_BEFORE_LABEL}}</div>
  </div>
  <div style="background:var(--surface-1);border-radius:var(--radius);padding:1rem;">
    <div style="font-size:13px;color:var(--text-secondary);margin-bottom:4px;">Typical task, 4 test runs</div>
    <div style="font-size:24px;font-weight:500;color:var(--text-primary);">{{TASK_AFTER_LABEL}}</div>
    <div style="font-size:13px;color:var(--text-muted);">was {{TASK_BEFORE_LABEL}} of waiting</div>
  </div>
</div>
<div style="display:flex;flex-wrap:wrap;gap:16px;margin-bottom:8px;font-size:12px;color:var(--text-secondary);">
  <span style="display:flex;align-items:center;gap:6px;"><span style="width:12px;height:12px;border-radius:2px;background:repeating-linear-gradient(45deg,#888780 0 2px,transparent 2px 5px);border:0.5px solid #888780;"></span>Before: the whole suite was the only option</span>
  <span style="display:flex;align-items:center;gap:6px;"><span style="width:12px;height:12px;border-radius:2px;background:#2a78d6;"></span>After: layered gates</span>
</div>
<div style="position:relative;width:100%;height:300px;">
  <canvas id="gateChart" role="img" aria-label="Horizontal bar chart of minutes per test run, before versus after: quick check {{BEFORE_MIN}} versus {{FAST_MIN}}, one subsystem {{BEFORE_MIN}} versus {{SUBSYSTEM_MIN}}, whole suite {{BEFORE_MIN}} versus {{BROAD_MIN}}">Minutes per run before versus after.</canvas>
</div>
<script src="https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.js"></script>
<script>
(function(){
  var cs = getComputedStyle(document.documentElement);
  var mode = document.documentElement.dataset.mode;
  var isDark = mode ? mode === 'dark' : matchMedia('(prefers-color-scheme: dark)').matches;
  var muted = (cs.getPropertyValue('--text-muted') || '').trim() || '#898781';
  var secondary = (cs.getPropertyValue('--text-secondary') || '').trim() || (isDark ? '#c3c2b7' : '#52514e');
  var grid = isDark ? '#2c2c2a' : '#e1e0d9';
  var pc = document.createElement('canvas'); pc.width = 8; pc.height = 8;
  var px = pc.getContext('2d'); px.strokeStyle = '#888780'; px.lineWidth = 2;
  px.beginPath(); px.moveTo(0, 8); px.lineTo(8, 0); px.stroke();
  var hatch = px.createPattern(pc, 'repeat');
  function fmt(v){ return v < 1 ? Math.round(v * 60) + ' s' : (Math.round(v * 10) / 10) + ' min'; }
  new Chart(document.getElementById('gateChart'), {
    type: 'bar',
    data: {
      labels: ['Quick check after an edit', 'One subsystem ({{SUBSYSTEM_NAME}})', 'Whole provider-free suite'],
      datasets: [
        { label: 'Before', data: [{{BEFORE_MIN}}, {{BEFORE_MIN}}, {{BEFORE_MIN}}], backgroundColor: hatch, barThickness: 18, borderRadius: 4, borderSkipped: 'start' },
        { label: 'After', data: [{{FAST_MIN}}, {{SUBSYSTEM_MIN}}, {{BROAD_MIN}}], backgroundColor: isDark ? '#3987e5' : '#2a78d6', barThickness: 18, borderRadius: 4, borderSkipped: 'start' }
      ]
    },
    options: {
      indexAxis: 'y', responsive: true, maintainAspectRatio: false,
      plugins: { legend: { display: false }, tooltip: { callbacks: { label: function(c){ return c.dataset.label + ': ' + fmt(c.parsed.x); } } } },
      scales: {
        x: { min: 0, max: {{AXIS_MAX}}, title: { display: true, text: 'minutes of wall time', color: muted, font: { size: 12 } }, grid: { color: grid, drawTicks: false }, border: { color: grid }, ticks: { color: muted, font: { size: 12 } } },
        y: { grid: { display: false }, border: { display: false }, ticks: { color: secondary, font: { size: 13 } } }
      }
    }
  });
})();
</script>
```

Values: `{{*_MIN}}` are decimal minutes (10 s = 0.17). `{{AXIS_MAX}}` is the before value rounded up a little. Labels are human strings ("10 s", "24 min").

### Visualization 2: what the runner collects versus what git tracks (SVG)

Loading messages: e.g. `["Counting what the runner can see", "Drawing the fence around the archives"]`. Title: `test_collection_vs_git_tracking`. Keep the coordinates; change only text.

```svg
<svg width="100%" viewBox="0 0 680 440" role="img"><title>What the test runner collects versus what git tracks</title><desc>The test directory holds {{ON_DISK}} modules on disk: {{TRACKED}} tracked in git and {{IGNORED}} gitignored but still collected. The fast gate reads {{FAST_FILES}} named tracked files, {{FAST_TESTS}} tests in {{FAST_LABEL}}. The broad gate reads everything on disk, {{BROAD_TESTS}} tests in {{BROAD_LABEL}}. Archives, backups and scratch directories are never collected.</desc>
<defs><marker id="arrow" viewBox="0 0 10 10" refX="8" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse"><path d="M2 1L8 5L2 9" fill="none" stroke="context-stroke" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round"/></marker></defs>
<g class="c-gray">
  <rect x="40" y="40" width="600" height="150" rx="20" stroke-width="0.5"/>
  <text class="th" x="340" y="62" text-anchor="middle" dominant-baseline="central">{{TEST_DIR}} on disk: {{ON_DISK}} modules</text>
</g>
<g class="c-teal">
  <rect x="60" y="84" width="270" height="86" rx="10" stroke-width="0.5"/>
  <text class="th" x="195" y="115" text-anchor="middle" dominant-baseline="central">Tracked in git</text>
  <text class="ts" x="195" y="139" text-anchor="middle" dominant-baseline="central">{{TRACKED}} modules</text>
</g>
<g class="c-coral">
  <rect x="350" y="84" width="270" height="86" rx="10" stroke-width="0.5"/>
  <text class="th" x="485" y="115" text-anchor="middle" dominant-baseline="central">Gitignored, still on disk</text>
  <text class="ts" x="485" y="139" text-anchor="middle" dominant-baseline="central">{{IGNORED}} modules, still collected</text>
</g>
<line x1="195" y1="170" x2="195" y2="238" class="arr" marker-end="url(#arrow)"/>
<line x1="485" y1="190" x2="485" y2="238" class="arr" marker-end="url(#arrow)"/>
<g class="node" onclick="sendPrompt('Show me the files in the fast gate and what each one protects')">
  <rect class="box" x="40" y="240" width="290" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="185" y="258" text-anchor="middle" dominant-baseline="central">Fast gate</text>
  <text class="ts" x="185" y="278" text-anchor="middle" dominant-baseline="central">{{FAST_FILES}} named files, {{FAST_TESTS}} tests, {{FAST_LABEL}}</text>
</g>
<g class="node" onclick="sendPrompt('Which of the gitignored test modules should be tracked, marked live, or deleted?')">
  <rect class="box" x="350" y="240" width="290" height="56" rx="8" stroke-width="0.5"/>
  <text class="th" x="495" y="258" text-anchor="middle" dominant-baseline="central">Broad gate or {{RAW_RUNNER}}</text>
  <text class="ts" x="495" y="278" text-anchor="middle" dominant-baseline="central">{{BROAD_TESTS}} tests, about {{BROAD_LABEL}}</text>
</g>
<g class="c-gray">
  <rect x="40" y="340" width="600" height="56" rx="8" stroke-width="0.5" stroke-dasharray="4 3"/>
  <text class="th" x="340" y="358" text-anchor="middle" dominant-baseline="central">Never collected ({{FENCE_SETTING}})</text>
  <text class="ts" x="340" y="378" text-anchor="middle" dominant-baseline="central">{{FENCED_DIRS}}</text>
</g>
</svg>
```

If the repo does not ignore tests by default, drop the coral box, widen the teal box to `x="60" width="560"` with its text at `x="340"`, and start the second arrow from the teal box instead. Keep subtitles under about 60 characters so they fit the 600px box.

## Follow-up run variant

A `followups` run changed truthfulness, not speed, so its report has a different shape. Under about 400 words of prose, in this order:

1. **Outcome in one sentence**, including HEAD at start, whether anything was committed, and how much of the budget was used.
2. **One block per item**, each with: the decision in one sentence; the two or three strongest pieces of evidence with `file:line` or commit hash; what changed; what was deliberately not changed and why. An inconclusive item reads `Confirm needed` and quotes the two competing authorities.
3. **Measured table**: every gate run, its count, and its wall time, with the broad gate once at the end and the delta in tests and files versus the first pass.
4. **Done / Optional / Parked.** Parked holds the product decisions (a fallback tightened into a refusal, backend support or retirement, a production module's deletion) with their prerequisites and where the plan is recorded.
5. **Files changed**, tracked versus ignored, and the pre-existing dirt left untouched.

Visualization 1 is optional here and used only when runtimes actually changed; Visualization 2 is replaced by a per-item decision table in the response text (item, claimants, authority that won, change made). Never invent a runtime figure for a run that was not timed.

## Markdown fallback (no visualize tool)

| Run | Before | After |
| --- | --- | --- |
| Quick check after an edit | {{BEFORE_LABEL}} | {{FAST_LABEL}} |
| One subsystem | {{BEFORE_LABEL}} | {{SUBSYSTEM_LABEL}} |
| Whole provider-free suite | {{BEFORE_LABEL}} | {{BROAD_LABEL}} |
| Failures an agent must read | {{FAILS_BEFORE}} | {{FAILS_AFTER}} |

| What the runner sees | Count |
| --- | --- |
| Test modules on disk | {{ON_DISK}} |
| Tracked in git | {{TRACKED}} |
| Gitignored but still collected | {{IGNORED}} |
| Fast gate | {{FAST_FILES}} files, {{FAST_TESTS}} tests |
| Broad gate | {{BROAD_TESTS}} tests |
