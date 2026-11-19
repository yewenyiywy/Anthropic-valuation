# Anthropic 估值 — 联合状态生命周期 DCF

[English](README.md) · **简体中文**

快照 2026-11-19 · 单位：十亿美元 · **发布门槛：BLOCKED**（[§3.1](#31-发布门槛)）：研究估计，非验证估值。

## 结果

| 均值 | P5 | **P10（悲观）** | **P50（基准）** | **P90（乐观）** | P95 | $P(V<0)$ |
|---:|---:|---:|---:|---:|---:|---:|
| 501.67 | 20.55 | **72.13** | **401.43** | **1,043.01** | 1,345.69 | 3.3% |

联合抽样 1,024 次（§1.5）。压力端点（所有参数块同时取一端，非分位数）：

| | $R_1$ | $R_5$ | $R_{10}$ | EV | $V$ |
|---|---:|---:|---:|---:|---:|
| 悲观 | 50.67 | 24.88 | 21.68 | −356.80 | −254.99 |
| 基准 | 100.12 | 221.47 | 328.27 | 392.82 | 494.63 |
| 乐观 | 115.69 | 396.70 | 734.42 | 2,760.30 | 2,862.11 |

反向 DCF，$V=1{,}200$（IPO 定价），每次只动一个参数：

| 参数 | 基准 | 所需 |
|---|---:|---:|
| $W$ | 8.86% | 5.67% |
| $g$ | 3% | 6.83% |
| $c^\ast$ | 45.5% | 10.8% |
| 全部朝乐观，$z$ | 0 | 0.47 |
| 份额、需求、获客、用量 | — | 达不到（最高 495–519） |

## 1. 模型

```math
V=\underbrace{\sum_{t=1}^{10}\frac{FCF_t}{(1+W)^t}}_{\S1.2}+\underbrace{\sum_{t>10}\frac{\mathbb E[FCF_t\mid R_{10}]}{(1+W)^t}}_{\S1.3}+\underbrace{Cash-Debt}_{\S1.4},\qquad \widehat V=\frac1{1024}\sum_{\ell}V^{(\ell)}\ (\S1.5)
```

### 1.1 收入

```math
R_t=s_t\,\mathcal R(L_t+T_t+S_t)+B^{p}_t,\qquad \mathcal R(X)=\sum_{idhv}X_{idhv}r_v,\qquad s_t=\min\Big(1,\frac{C_t}{\mathcal R(L_t+T_t+S_t)}\Big)
```

| 符号 | 含义 | 取值 |
|---|---|---|
| $L,T,S$ | 正式 API、试点、企业席位的账单张量 | §1.1.2 |
| $r_v$ | 各供应商状态下 Claude 的收入份额 | $(1,.6,0,0,0,0,0)$ |
| $C_t$ | 企业需求天花板 | §1.1.5 |
| $B^p_t$ | 个人订阅 | §1.1.6 |

#### 1.1.1 起点

```math
R_0=81,\qquad \omega=\tfrac{26.300}{33.242}=79.1\%,\qquad A_0=\omega R_0=64.1,\qquad B_0=(1-\omega)R_0=16.9,\qquad B^p_0=0.5B_0
```

来源：[S-1](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074338/anthropicpbc-sx1ax3.htm)、[年化收入](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074628/anthropicpbc-fwpjapanprospa.htm)。10 月结构沿用前 9 个月（代理）。

#### 1.1.2 客户状态张量

```math
X_t=\mathcal K_{Z_t}\big(\mathcal G_t(X_{t-1})\,M_{Z_t}\big)+A_t,\qquad X\in\mathbb R^{8\times3\times3\times7}_{(i,d,h,v)}
```

$i$ 生命周期（种子 0–4+、成长、中小企业、大型）· $d$ 停留期 · $h$ 健康度 · $v$ 供应商 · $Z_t$ 宏观状态。

**1.1.2.1 生命周期核 $\mathcal K$**

```math
g_k=\frac{F_k-F_{k-1}}{U_{k-1}},\quad U_k=U_{k-1}(1-g_k-b_k-h_k),\quad h^{\mathrm{eff}}_i=\min(0.95,\,h_i\,m^Z_{\mathrm{death}}m^H_{\mathrm{death}})
```

| | 取值 |
|---|---|
| $F_{1..4}$（种子→A 轮） | 10 / 22 / 31 / 36% |
| $h_i$（早期/成长/中小/大型） | 15.03 / 8.06 / 7.27 / 0.132%（BLS） |
| $m^Z_{\mathrm{death}}$、$m^Z_{\mathrm{grow}}$（寒冬/正常/繁荣） | 1.5/1/0.75 · 0.65/1/1.25 |
| $m^H_{\mathrm{death}}$、支出（困境/有融资/自给） | 1.6/1/0.55 · 0.75/1/1.10 |

**1.1.2.2 健康度** $\;\pi_{h\mid y}\propto\pi_hP(y\mid h)$, $P(y{=}1\mid h)=(.15,.75,.25)$.

**1.1.2.3 宏观** $\;P_Z=\begin{pmatrix}.60&.35&.05\\.18&.67&.15\\.08&.42&.50\end{pmatrix}$ （寒冬、正常、繁荣）。

**1.1.2.4 供应商**

```math
c=\Big(1-\frac{s_g}{1-h_g}\Big)m^Z_c,\qquad M_{i\to w}=\begin{cases}c\,\delta_w&\text{流失至 }w\\(1-c)\sigma&\text{单}\leftrightarrow\text{多供应商}\\(1-c)(1-\sigma)&\text{保持}\end{cases}
```

$s_g$ = 69.0/78.7/82.6/92.3% · $\delta$ = .35/.25/.15/.10/.15 （OpenAI、Google、自建、其他、不用）· $\sigma$ = .12 / .04 · $m^Z_c$ = 1.3 / 0.85 · 回流每年 .06 / .035。

#### 1.1.3 增长

```math
d_t=\max\Big(0,1-\tfrac{t-1}{7}\Big),\quad \mu_t=[1-(1-p)d_t][1+(q-1)d_t],\quad \alpha_t=.1+.5d_t
```

```math
L_t=\mathcal K\big([(L_{t-1}+\phi\rho T_{t-1})F_t\mu_tH]M\big)+(1-\alpha_t)A_t,\quad T_t=\alpha_tA_t,\quad S_t=\mathcal K\big([S_{t-1}F_t(1+bd_t)H]M\big)+A^{s}_t
```

基准：$p$=.78, $q$=1.65, $\phi$=.35, $\rho$=3, $b$=12%, $F_t=1+(f-1)d_t$.

#### 1.1.4 新客户

```math
J_t=x_Z\big[n\,d_t\,\mathcal R(X_{t-1})+\eta(1-d_t)\textstyle\sum X r_v(1-s_i)\big],\qquad J^{\mathrm{birth}}_t=\min(0.2J_t,\,0.418)
```

$n$=.20, $\eta$=1; $0.418=5049\times2\times.75\times.25\times5\%\times\overline{\text{seed round}}$.

#### 1.1.5 企业需求天花板

```math
C_t=c_t\sum_iD_{i,t},\quad D_{i,t}=D_{i,t-1}\big[1.03+(mg_i-.03)\max(0,1-\tfrac{(t-2)^+}{8})\big],\quad c_t=c_0+(c_{10}-c_0)\min(\tfrac t{10},1)
```

$D_{i,0}=176.8\,w_i$ （[Menlo](https://menlovc.com/perspective/2026-the-state-of-enterprise-ai/) × IDC 权重） · $g_i$ IDC 2024–28 CAGR · $m$=.7/1/1.5 · $c_0=(81-B_0/2)/176.8=41\%$ · $c_{10}$=15%/41%/50%.

#### 1.1.6 个人订阅

```math
B^p_t=\min\Big(B^{\mathrm{raw}}_t\tfrac{1-\kappa e_t}{1-\kappa e_0},\;R_C+(B^p_0-R_C)^+(1-\tfrac t5)^+\Big),\qquad R_C=12N_NkF_C
```

$\kappa$=.8/.5/.2 · $e_t$: .4→.8/.7/.6 · $N_N$=0.325B ([Netflix](https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm)) · $k$=5/15/30% · $F_C$=\$13.53/mo.

### 1.2 自由现金流，$t\le10$

```math
Y_t=R_t-\max(K_t,\,c_tR_t)-(o_t+x_t)R_t,\qquad FCF_t=Y_t-0.25\,Y_t^+,\qquad \theta_t=\theta^\ast+(\theta_0-\theta^\ast)2^{-t/H}
```

| 符号 | 取值 |
|---|---|
| $\theta=(c,o,x)$ | 算力、其他运营费用、资本开支占收入比 |
| $\theta_0$ | (56.6%, 47.2%, 2.8%)，2026 年前 9 个月披露值 |
| $\theta^\ast$ | 基准 (45.5%, 24.0%, 6%)，来自可比公司（§3.6） |
| $H$ | 3 y (§3.2) |
| $K_t$ | 算力承诺下限： $K_1$=70.7, $K_{2..4}$=126.97, $K_{5..19}$=29.95, $K_{20+}$=0 |

### 1.3 延续价值，$t>10$

```math
a_{10}=(R_{10},0,0,0),\quad a_t=a_{t-1}P\,\mathrm{diag}\big(k(1+g),.85k,1.08k(1+g),0\big),\quad \mathbb E[FCF_t]=a_t\mu-S_t\Big(K_t-\tfrac{c\,\mathbf 1^\top a_t}{S_t}\Big)^+
```

```math
P=\begin{pmatrix}1-e-\delta-u&\delta&u&e\\.10&.90-e-u&u&e\\.40&\delta&.60-e-\delta&e\\0&0&0&1\end{pmatrix},\quad \mu=\big(m,.2m,\min(.6,\tfrac43m),0\big),\quad m=.75(1-c^\ast-o^\ast-x^\ast)
```

状态：成熟、衰退、再增长、退出。$k$ 使存活者长期增速等于 $g$。30 年以后： $a_{30}B(I-B)^{-1}\mu/(1+W)^{30}$, $B=A/(1+W)$.

| | 悲观 | 基准 | 乐观 |
|---|---:|---:|---:|
| $e=[1-.92^{1/5}]\varsigma$ （仅困境退出） | .00827 | .00132 | .0009 |
| $\delta$ / $u$ | .30 / .03 | .20 / .08 | .10 / .15 |
| $m$ | 8.9% | 18.4% | 27.9% |

$\varsigma$：8%（[Daepp et al.](https://doi.org/10.1098/rsif.2015.0120)），悲观 50%（互联网泡沫）。5 年 8% 退市率： [BCG](https://www.bcg.com/publications/2026/why-do-companies-fail-us-failure-rates).

### 1.4 股权衔接

```math
Cash-Debt=212.684-110.873\quad(\text{调整后 }232.351-109.742\text{，多 }20.80)
```

稀释尚未确定。

### 1.5 不确定性

```math
(n_r,n_m)\sim\mathcal N\Big(0,\begin{pmatrix}1&\rho\\\rho&1\end{pmatrix}\Big),\quad n_w\sim\mathcal N(0,1),\quad z_\ell\sim\mathrm{Tri}(-1,0,1),\quad Z_t\sim P_Z
```

```math
z_r=\frac{n_r}{1.2816}\bar z_{\pm},\qquad m^\ast=\hat F_m^{-1}(\Phi(n_m)),\qquad W=\hat F_W^{-1}(\Phi(n_w))
```

| 符号 | 取值 |
|---|---|
| $\bar z_{\pm}$ | −0.312 / +0.630：使 $R_5/R_1$ = 基准 × (1.28, 2.38)/1.80，即 ≥500 亿美元可比公司 4 年收入倍数 q10、q90 与 q50 之比 |
| $\hat F^{-1}_m,\hat F^{-1}_W$ | 可比公司经验分位数（§3.6） |
| $\rho$ | .334（收入增长与利润率变化的 Spearman 相关 .32） |
| $z_\ell$ | 生命周期块：$g$、$e$、$\delta$、$u$（手设） |

仅宏观：均值 402.88，P5–P95 242.27–519.67。单一共同因子：P90 1,177.01。

## 2. 参数

| | 悲观 | 基准 | 乐观 | 来源 |
|---|---:|---:|---:|---|
| 早期 / 成长 / 中小 / 大型 | 30/30/25/15% | 15/25/30/30% | 5/15/30/50% | 手设 |
| 试点占比；成功率 / 推广年数 | 25%; .20/2 | 30%; .35/3 | 20%; .50/4 | 手设 |
| 用量 $q$ / 价格 $p$ | 1.45/.65 | 1.65/.78 | 1.85/.88 | 手设 |
| 获客 $n$ / 替补 $\eta$ | .10/.50 | .20/1 | .30/1.25 | 手设 |
| 订阅增长 $b$ | 3% | 12% | 22% | 手设 |
| $c^\ast$ / $o^\ast$ / $x^\ast$ | .589/.233/.06 | .455/.240/.06 | .345/.233/.05 | §3.6（$x^\ast$ 手设） |
| $c_{10}$ | 15% | 41% | 50% | 手设 |
| $g$ | 2.5% | 3% | 3.5% | 手设 |
| $W$ | 9.38% | 8.86% | 7.68% | §3.6 |

## 3. 证据

除标明“只评分一次”外，以下均为开发或诊断证据。

### 3.0 数据

| 数据集 | 核对方式 | 结果 |
|---|---|---|
| §3.2–3.4 的 SEC 数字 | XBRL 原始版本 vs 申报原文 | 205/205 一致（[记录](data/sec_reconciliation.csv)） |
| 收购事件 | 两个独立来源 | 除 NetSuite 股权价值外全部（[事件](data/stage4_exit_events.csv)） |
| 原有数据 | 申报原文；市值用第二网站 | SEC 295/295 一致；PayPal 现金已修正（13.002→13.083）；替换 8 个失效链接（[记录](data/legacy_reconciliation.csv)） |
| 待核 | — | IDC 分行业、JPM/ITU、Cisco/CMGI/VeriSign 1998–99 |

### 3.1 发布门槛

```math
\text{发布}\iff N_{\text{fam}}\ge10\ \wedge\ N_{\text{cycle}}\ge2\ \wedge\ \mathrm{WAPE}_V\le30\%\ \wedge\ |\mathrm{bias}_V|\le15\%\ \wedge\ \mathrm{WAPE}_V<\min(\text{市值不变},\ \text{市销率不变})
```

当前阻塞项（`python -m evaluation.validation_gate --audit`）：

| # | 阻塞项 | 状态 |
|---|---|---|
| 1 | 未触碰的最终测试 | cloud2018 名单规则已冻结（[规则](evaluation/final2018/roster_rule.md)）；名单未选出 |
| 2 | 完整模型按市值误差训练 | 未开始 |
| 3 | 经验证的公司画像（12 项输入） | 0 / 17 |
| 4 | 生产模型合同与运行轨迹 | 未开始 |
| 5 | 冻结清单、独立复核人 | 复核人未指定 |

被收购公司按成交时支付的股权价值、在期限 $\max(1,\mathrm{round}(\tau))$ 评分（[规则](evaluation/acquisition_endpoint_policy.md)，已批准）。

### 3.2 利润率路径

```math
m=\frac{CFO-\text{资本开支}-\text{资本化软件}}{\text{收入}}
```

第 4 阶段，只评分一次（[预注册](evaluation/stage4_margin_preregistration.md)、[评分](evaluation/stage4_margin_score.json)），11 家，MAE（百分点）：

| 模型 | 开发留一 | 第 4 阶段 | 2015 | 2020 |
|---|---:|---:|---:|---:|
| 维持 | 9.64 | 23.44 | 18.60 | 25.26 |
| 渐变到 15% | 11.12 | 15.07 | 13.39 | 15.69 |
| 样本均值 | 9.28 | 8.63 | 11.45 | 7.57 |
| 收敛，$H$=3 | 8.56 | **6.77** | 10.10 | 5.52 |
| 杠杆（预注册选择） | **4.94** | 8.87 | 5.99 | 9.94 |

预注册选择未采用（输给样本均值）。18 个观测扣 SBC 后：中位数 11.1%，P90 24.4%；$H$=3 收敛到 18.1% 的留一误差 7.26，维持为 16.56。

### 3.3 增长与退出

```math
g_t=g_\infty+(g_0-g_\infty)2^{-t/H_g},\qquad \ln\tfrac{R_h}{R_0}=\textstyle\sum_{t\le h}g_t
```

| 留一 MAE，对数收入（18 个） | 不变 | 维持 $g_0$ | 引擎渐变 | 拟合 $H_g$=4、$g_\infty$=6.5% |
|---|---:|---:|---:|---:|
| | 1.436 | 0.660 | 0.242 | 0.221 |

Anthropic $g_0\approx2.57$，面板最大 0.63：超出样本范围。

| 5 年名单 | n | 被收购 | 破产 |
|---|---:|---:|---:|
| 云 2015 | 10 | 5 | 0 |
| 云 2020 | 14 | 1 | 0 |
| 互联网 1999 | 18 | 2 | 2 |

收购价为此前市值的 1.0–2.2 倍 ⇒ $e$ 只计困境退出。

### 3.4 市值回测，云 2020（已暴露，诊断）

| | 模型 | 市值不变 | 市销率不变 |
|---|---:|---:|---:|
| $V$ WAPE / 偏差 | 71.17% / −49.37% | 58.82% / +17.73% | 124.89% / +124.89% |
| $V$ Spearman | −0.3 | −0.6 | −0.6 |
| $R$ / FCF WAPE | 16.25% / 37.91% | — | — |

基本面准，估值倍数不准（2025 年 P/FCF 10–104 倍）。

### 3.5 其他实验（均未采用）

| 实验 | 结果 |
|---|---|
| 1999 年预测 FY2000 | MAPE 21.54%（不变 50.23%） |
| 5 年饱和模型，按公司留一 | WAPE 41.08%（不变 61.19%） |
| 外部 1999 样本 | WAPE 60.21%（不变 69.97%） |
| 联合引擎，聚合约束版 | $V$ WAPE 86.19% |
| 市值误差训练迁移 | 88.48 / 61.40 / 65.63%（不变 58.82%） |

敏感性，基准 494.63：去健康度 317.36 · 去停留期 499.11 · 去供应商 404.64 · 全关 259.22 · 寒冬/繁荣 145.51/524.66 · 成本立即到位 583.92 · $H$=6.8：417.5。

### 3.6 可比公司校准（[预注册](evaluation/margin_scale_preregistration.md)）

**5 年后利润率**，368 个公司-年，39 个公司族，按族留一（[面板](data/margin_scale_panel.csv)，有幸存者偏差）：

| 维持 | 均值 | **线性** | 收敛 | 岭回归 | GBM | GP | MLP |
|---:|---:|---:|---:|---:|---:|---:|---:|
| 11.14 | 15.35 | **9.24** | 9.56 | 10.03 | 10.48 | 12.39 | 11.38 |

MAE（百分点）。ML 均未胜过线性 ⇒ 不采用。线性：$m_{t+5}=.60\,m_t+.108$ ⇒ 长期 27.1%，半衰期 6.8 年。

**长期利润率**

```math
m^\ast_i=\tfrac13\textstyle\sum_{t=T-2}^{T}\mathrm{OI}_{it}/R_{it},\quad i\in\{\text{平台公司},\ R\ge20\},\qquad (c^\ast,o^\ast)=(1-m^\ast)(s,\,1-s)
```

$m^\ast$：MSFT 45.7、微软智能云 42.2、Meta 39.4、Adobe 34.1、AWS 33.2、Alphabet 30.5、Oracle 30.1、Netflix 25.6、Intuit 25.3、Salesforce 17.8、Google Cloud 14.3% ⇒ P10/P50/P90 = 17.8/30.5/42.2%。$s$ = 微软智能云 营业成本/(营业成本+运营费用)，FY24–26 = 59.6/65.1/71.6%。

**折现率**

```math
\beta_u=\frac{\beta_L}{1+(1-t)D/E},\qquad W=\tfrac{E}{D+E}\big[r_f+\beta_u(1+(1-t)\tfrac DE)\,\mathrm{ERP}\big]+\tfrac{D}{D+E}(r_f+1\%)(1-t)
```

$r_f$=5.0%，ERP=4.14%（Damodaran，2026 年 9 月），13 家可比 β（[输入](data/wacc_inputs.csv)），$D/E$=0.09 ⇒ $\beta_u$ 取 P75/P50/P25 时 $W$ = 9.38/8.86/7.68%。ERP 3.56/6.05% ⇒ 8.31/10.65%。

| 基准 $V$ | |
|---|---:|
| 原手设（$c^\ast$ .48，$o^\ast$ .25，$W$ 12%） | 249.22 |
| + 估计成本 | 292.5 |
| 仅估计 $W$ | 421.1 |
| 两者 | 494.63 |
| 收入中心调到可比中位数 $R_5/R_1$=1.80（未采用） | 293.1 |

乐观修正：各块单独取 P90 为 904.6（收入）、755.4（利润率）、643.7（$W$）、608.3（生命周期）；同时取极端 2,905；分块独立抽样 P90 为 1,043.01。

## 4. 复现

```bash
pip install numpy scipy scikit-learn
python -m unittest discover -s evaluation -p 'test_*.py'   # 136 项测试
python -m evaluation.validation_gate --audit
python -m models.joint_customer_states
python -m evaluation.reverse_dcf --equity 1200
python -m evaluation.margin_scale
python -m evaluation.margin_path --verify
python -m evaluation.cloud_equity
```

[data/README.md](data/README.md) · [MODEL_VALIDATION_PROTOCOL.md](MODEL_VALIDATION_PROTOCOL.md) · [AGENTS.md](AGENTS.md)
