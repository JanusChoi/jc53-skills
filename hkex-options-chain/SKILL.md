---
name: hkex-options-chain
description: |
  港股个股正股期权链（Single Stock Equity Options）数据获取与分析，基于 HKEX 官方 stock_options_search.aspx AJAX 端点。
  触发：用户提到港股期权、个股期权、call / put 行权价、隐含波动率 IV、未平仓合约 OI、买卖价差、希腊字母，或任何"XX 期权链""XX Call/Put""查某港股的期权"类查询时使用。
  适用：任意在 HKEX 上市的个股期权标的（恒生指数成分股、热门科技股、银行股等约 139 个支持标的），不限定特定股票代码。
  也用于：已知到期日 + 标的的港股正股期权，盘中查权、复盘、生成报告。
  不用于：衍生权证（DW / 窝轮）—— 那是另一套产品，用券商软件或港交所其他页面。
---

# HKEX Stock Options Chain Skill

> 定位：**港交所个股正股期权链（Single Stock Equity Options）的稳定数据获取 + 分析**。
> **核心经验**：HKEX 页面有 dialog 死循环 + slider keyword 校验——**别用 UI 交互，绕到 AJAX 端点直连**。

## Inputs to collect

- **标的代码**（必填）：5 位港股代码（0700 / 9988 / 9999 等）
- **到期日**（必填）：YYYY-MM-DD 格式
- **wtype**（可选）：C / P / 空（默认空=All）
- **moneyness 范围**（可选）：-15 / 15（默认 = ±15% moneyness 范围）
- **premium 范围**（可选）：0 / 11（默认 = 0-11% premium）
- **HKATS Code**（必填输出）：标的的港交所代号（0700=TCH，9988=ALB，9999=NTE）

## 关键事实（**踩坑沉淀**）

### 1. HKEX 端点（**核心**）

不是浏览器 UI 交互，是**直接 POST 到 search 端点**：

```bash
curl -sS -X POST \
  "https://www.hkex.com.hk/eng/sorc/options/stock_options_search.aspx" \
  -d "action=ajax&type=search&otype=ucode&code={CODE}&wtype={C/P/空}&mdate={YYYY-MM-DD}&moneyness1={OTM度数}&moneyness2={ITM度数}&premium1=0&premium2=11&ordering=ucode_asc&page=1" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Referer: https://www.hkex.com.hk/eng/sorc/options/stock_options_search.aspx"
```

**完整参数（来自 stock_options_search.js 源码）：**

| 参数 | 含义 | 取值 |
|------|------|------|
| `otype` | 标的类型 | `ucode` / `hcode` |
| `code` | 标的值（ucode 或 hcode）| 5 位代码 或 HKATS code |
| `wtype` | C=Call / P=Put / 空=All | `C` / `P` / `""` |
| `mdate` | 到期日 | `YYYY-MM-DD` |
| `moneyness1` | **OTM 度数**（slider 右手柄，负值）| `-15` 表示 15% OTM |
| `moneyness2` | **ITM 度数**（slider 左手柄，正值）| `15` 表示 15% ITM |
| `premium1` / `premium2` | 权利金范围（占正股价格 %）| `0` / `11` |
| `ordering` | 排序 | `ucode_asc` |
| `page` | 分页（10 条/页）| `1` |

### 2. moneyness 字段**方向反直觉**

`moneyness1` 是 OTM 度数（slider 右手柄，**负值**），`moneyness2` 是 ITM 度数（左手柄，**正值**）。**实际值取负数**。

- 想看 5% OTM + 5% ITM：`moneyness1=-5, moneyness2=5`（即默认 5%）
- 想看 15% OTM + 15% ITM：`moneyness1=-15, moneyness2=15`
- 想看 30% OTM + 30% ITM：`moneyness1=-30, moneyness2=30`（但 HKEX 端最大 ±16）

### 3. wtype 必须分开请求

**如果 wtype=空，一次只返回 Call 链**。**Put 链必须单独 wtype=P 请求**。**别用 wtype=空 + 期望 Call+Put 一起**——HKEX 端逻辑是 All = Call only（这是 1.5 小时死磕的教训）。

### 4. 不能用 HKEX 页面 UI 抓的 3 个原因

- ❌ **alert 死循环**：search 按钮的 JS 校验会反复弹 "Please enter the search keyword"
- ❌ **moneyness slider 校验**：moneyness textbox 写 "30% ITM to 30% OTM" 不被识别为合法 keyword（HKEX 把 slider 数值映射到 keyword 列表）
- ❌ **dialog 阻塞 eval**：任何 alert 弹出会导致后续 `browser_evaluate` 一致不返回

**唯一可靠**：直接 POST 到 AJAX 端点，绕开所有 UI/JS 校验。

### 5. 响应数据格式

返回的是 HTML 片段（非 JSON），需要用正则解析。**每行 19 个 `<td>`**：

```html
<tr>
  <td>Option Calculator link</td>
  <td>Option Chart link</td>
  <td>Option Detail link</td>
  <td>Underlying Code</td>      <!-- 09988 -->
  <td>Underlying Name</td>      <!-- Alibaba -->
  <td>HKATS Code</td>           <!-- ALB -->
  <td>Call / Put</td>           <!-- C or P -->
  <td>Expiry (D/M/Y)</td>       <!-- 29/06/26 -->
  <td>Strike</td>               <!-- 110.00 -->
  <td>Last Price</td>           <!-- 5.600 -->
  <td>Price Change</td>         <!-- -2.450 -->
  <td>Moneyness</td>            <!-- 2.83% ITM -->
  <td>IV (%)</td>               <!-- 42.94 -->
  <td>HV 30 (%)</td>            <!-- 45.33 -->
  <td>Delta (%)</td>            <!-- 60.30 -->
  <td>Effective Gearing (x)</td><!-- 12.19 -->
  <td>Option Premium (%)*</td>  <!-- 4.95 -->
  <td>Volume</td>               <!-- 1028 -->
  <td>Previous Day OI</td>      <!-- 825 -->
</tr>
```

`N/A` 或 `-` 表示无数据/无成交（特别是深度 OTM）。

## Procedure

### Step 1：选定参数

- 用户提供标的代码 → 找 HKATS Code
- 列出 HKATS Code 表（常用）：

| 标的 | HKATS Code |
|------|-----------|
| 腾讯 0700 | TCH |
| 阿里 09988 | ALB |
| 美团 03690 | MET |
| 小米 01810 | MIU |
| 京东 09618 | (查) |
| 网易 09999 | NTE |
| 百度 09888 | (查) |

### Step 2：构造 curl 命令（**主流程**）

```bash
# Call 链
curl -sS -X POST \
  "https://www.hkex.com.hk/eng/sorc/options/stock_options_search.aspx" \
  -d "action=ajax&type=search&otype=ucode&code=09988&wtype=C&mdate=2026-06-29&moneyness1=-15&moneyness2=15&premium1=0&premium2=11&ordering=ucode_asc&page=1" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Referer: https://www.hkex.com.hk/eng/sorc/options/stock_options_search.aspx" \
  -o /tmp/{CODE}_call.html

# Put 链
curl -sS -X POST \
  "https://www.hkex.com.hk/eng/sorc/options/stock_options_search.aspx" \
  -d "action=ajax&type=search&otype=ucode&code=09988&wtype=P&mdate=2026-06-29&moneyness1=-15&moneyness2=15&premium1=0&premium2=11&ordering=ucode_asc&page=1" \
  -H "X-Requested-With: XMLHttpRequest" \
  -H "Referer: https://www.hkex.com.hk/eng/sorc/options/stock_options_search.aspx" \
  -o /tmp/{CODE}_put.html
```

### Step 3：解析 HTML → 表格数据

```python
import re
import json

def parse_hkex_options_html(html):
    html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
    rows = re.split(r'<tr[^>]*>', html)
    parsed = []
    for r in rows:
        if 'ALB' not in r and '09988' not in r:  # 过滤非目标行
            continue
        tds = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
        cells = [re.sub(r'<[^>]+>', '', td).replace('&nbsp;', '').strip() for td in tds]
        parsed.append(cells)
    return parsed

# 提取关键字段
def extract(rows, code='09988'):
    out = []
    for r in rows:
        # 索引: 3=Code, 6=C/P, 8=Strike, 9=Last, 12=IV, 13=HV30, 14=Delta, 17=Volume, 18=OI
        if len(r) > 18 and r[3] == code:
            out.append({
                'type': r[6],         # C / P
                'strike': r[8],
                'last': r[9],
                'change': r[10],
                'moneyness': r[11],
                'iv': r[12],
                'hv30': r[13],
                'delta': r[14],
                'eff_gearing': r[15],
                'premium_pct': r[16],
                'volume': r[17],
                'oi': r[18],
            })
    return out
```

### Step 4：抓 4 个核心衍生指标

- **IV 区间**：所有有值 IV 的 min / max / 中位数
- **OI 集中区**：所有 OI > 5000 的行（"大资金集中区"）
- **流动性最深的 ATM**：Volume × OI 最高的 ATM 区域合约
- **Put/Call OI 比**：所有 Put OI 合计 / 所有 Call OI 合计

### Step 5：写到报告

按 equity-snapshot / market-brief skill 模板输出。重点 6 段：
1. 一句话核心（卖方/买方 + OI 集中 + IV 位置）
2. 估值快照（含 IF 标准、HV 30、ATM IV）
3. 业绩快照（4 财年）
4. 资金/技术面
5. 催化日历
6. 风险提示

## Output contract

**主交付物**：
- **JSON 数据**：`{code}_chain.json`（解析后的表格）
- **人类可读报告**：markdown 或 HTML（看用户场景）

**强制字段**：
- 数据时点（精确到分钟）
- 标的 + HKATS Code
- 到期日
- IV / HV 30 / Delta / OI 全部保留
- moneyness 范围声明
- "数据来源 HKEX stock_options_search.aspx AJAX 端点"

**不要**：
- ❌ 不要试图用 Playwright 跑 search 按钮
- ❌ 不要相信页面 UI 显示的默认 5% 就是"完整链"——HKEX 端会按 moneyness 切
- ❌ 不要把 Call 和 Put 用 wtype=空 一次拉——必须分两次

## Failure handling

| 情况 | 应对 |
|------|------|
| curl 返回空 | 检查 `code` 5 位是否在 HKEX 个股期权列表（`ucode` 139 个标的中） |
| moneyness=-15 但只有 10 行 | HKEX 端 ±15% 范围就 10 个行权价（按正股价格自动分布） |
| 深度 OTM 的 IV 显示 N/A | 正常——无成交，HKEX 不计算 IV |
| Put 链 wtype=P 后 Price 显示负数 | 检查 Price Change 字段，负数 = 跌，正数 = 涨 |
| curl 返回 403/401 | 加 `User-Agent` header + `Accept: */*` |
| 标的找不到 HKATS Code | 用 `ucode` 模糊匹配：`grep -i "Alibaba" /tmp/ucode_list.txt` |

## Examples

### Example 1：抓 9988 6/29 完整 Call + Put 链

```bash
# Call
curl -sS -X POST "https://www.hkex.com.hk/eng/sorc/options/stock_options_search.aspx" \
  -d "action=ajax&type=search&otype=ucode&code=09988&wtype=C&mdate=2026-06-29&moneyness1=-15&moneyness2=15&premium1=0&premium2=11&ordering=ucode_asc&page=1" \
  -H "X-Requested-With: XMLHttpRequest" \
  -o /tmp/9988_call.html

# Put
curl -sS -X POST "https://www.hkex.com.hk/eng/sorc/options/stock_options_search.aspx" \
  -d "action=ajax&type=search&otype=ucode&code=09988&wtype=P&mdate=2026-06-29&moneyness1=-15&moneyness2=15&premium1=0&premium2=11&ordering=ucode_asc&page=1" \
  -H "X-Requested-With: XMLHttpRequest" \
  -o /tmp/9988_put.html
```

### Example 2：抓 0700 7/30 远月（验证流动性 vs 6/29）

```bash
curl -sS -X POST "https://www.hkex.com.hk/eng/sorc/options/stock_options_search.aspx" \
  -d "action=ajax&type=search&otype=ucode&code=00700&wtype=&mdate=2026-07-30&moneyness1=-10&moneyness2=10&premium1=0&premium2=11&ordering=ucode_asc&page=1" \
  -H "X-Requested-With: XMLHttpRequest" \
  -o /tmp/0700_2026-07-30.html
```

### Example 3：用 Python 一键抓 + 解析

```python
import subprocess, re, json

def fetch_chain(code, mdate, moneyness=15):
    """HKEX 个股期权链抓取（Call + Put 两次）"""
    result = {'call': [], 'put': []}
    for wtype, key in [('C', 'call'), ('P', 'put')]:
        data = (
            f"action=ajax&type=search&otype=ucode&code={code}"
            f"&wtype={wtype}&mdate={mdate}"
            f"&moneyness1=-{moneyness}&moneyness2={moneyness}"
            f"&premium1=0&premium2=11&ordering=ucode_asc&page=1"
        )
        cmd = [
            'curl', '-sS', '-X', 'POST',
            'https://www.hkex.com.hk/eng/sorc/options/stock_options_search.aspx',
            '-d', data,
            '-H', 'X-Requested-With: XMLHttpRequest',
            '-H', 'Referer: https://www.hkex.com.hk/eng/sorc/options/stock_options_search.aspx'
        ]
        html = subprocess.run(cmd, capture_output=True, text=True).stdout
        html = re.sub(r'<!--.*?-->', '', html, flags=re.S)
        rows = re.split(r'<tr[^>]*>', html)
        for r in rows:
            if code not in r:
                continue
            tds = re.findall(r'<td[^>]*>(.*?)</td>', r, re.S)
            cells = [re.sub(r'<[^>]+>', '', td).replace('&nbsp;', '').strip() for td in tds]
            if len(cells) > 18 and cells[3] == code:
                result[key].append({
                    'type': wtype,
                    'strike': cells[8],
                    'last': cells[9],
                    'change': cells[10],
                    'moneyness': cells[11],
                    'iv': cells[12],
                    'hv30': cells[13],
                    'delta': cells[14],
                    'eff_gearing': cells[15],
                    'premium_pct': cells[16],
                    'volume': cells[17],
                    'oi': cells[18],
                })
    return result

# 抓 9988 6/29
chain = fetch_chain('09988', '2026-06-29', moneyness=15)
print(f"Call 行数: {len(chain['call'])}")
print(f"Put 行数: {len(chain['put'])}")
print(f"120 Put OI: {[c['oi'] for c in chain['put'] if c['strike'] == '120.00']}")
```

## 关键经验（**写给未来的自己**）

1. **永远用 curl 直连 AJAX 端点**——HKEX 页面 UI 死磕 1.5 小时得出的结论
2. **Call + Put 必须分两次**——wtype=空 只返回 Call
3. **moneyness1/2 方向反直觉**——1 是 OTM 度数（取负），2 是 ITM 度数（取正）
4. **HKEX 个股期权端点**：`stock_options_search.aspx`（不是 `equity-options`、不是 `cbbc/search`、不是 `eng/products/...`）
5. **5% 默认范围只显示 7-10 个行权价**——要看完整链必须用 -15 / 15 或更大
6. **HKATS Code 必备**——报告里没写 HKATS Code 视为不专业
7. **HV 30 字段**——HKEX 自动算好，HV 30 = 实际 30 日波动率（不是预测 IV）
8. **Put/Call OI 比**——如果 Put OI >> Call OI，市场情绪偏空（防下跌），策略偏卖 Call
9. **深度 OTM 的 IV 通常 N/A**——HKEX 不显示
10. **别用 browser_snapshot 抓数据**——snapshot 是 YAML，解析后内容顺序会变。用 curl 拿 HTML 然后 Python 正则解析

## 关联 Skill

- `equity-snapshot`：用此 skill 抓到的链数据，套 equity-snapshot 模板输出 1 页报告
- `earnings-flash`：业绩点评用
- `thesis-tracker`：跟踪投资逻辑用
- `market-brief`：盘前/盘后简报用
