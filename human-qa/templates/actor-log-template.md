# Actor log

- Persona:
- Target:
- Cases in scope: C1, C2, …
- Started:

规则：每步先写预期，再操作；结束时必须有 STEP 标记行。尽量在标题里带 case id + 探针（如 `C3 · INV-CARD · 换模型后单发`）。流式/多模型必做基数与停止/刷新计数。

---

## Step step-01 — C? · INV-? · <标题>

**预期（操作前）：** …；期望 delta：`<metric>=0或1`

```
STEP_START|step-01|C? · INV-? · <标题>
```

**操作前计数：**

```
COUNT|before|assistant_bubbles_total=<n>
COUNT|before|generating_indicators=<n>
```

**操作：** …

**观察 / 证据：** URL=…；可见文案=…；截图=`screens/…`

```
COUNT|after|assistant_bubbles_total=<n>
COUNT|after|generating_indicators=<n>
COUNT|delta|assistant_bubbles_total=<n>
```

```
STEP_DONE|step-01|…证据…
```

或

```
ASSERTION_FAILED|step-01|category=app-bug; domain=general; expected=…; actual=…; url=…; evidence=…; repro=…; likely-scope=…; next-agent-prompt=…
```

---

## Step step-02 — …

（同上）

---

```
RUN_COMPLETED|passed|failed|incomplete|<一行：覆盖了哪些 case、发现了什么、阻塞、给 Judge 的要点>
```
