# Anthropic 估值 — 联合状态生命周期 DCF

[English](README.md) · **简体中文**

快照日期 2026-11-19。除特别说明外，单位为十亿美元。**研究模型：[发布门禁](MODEL_VALIDATION_PROTOCOL.md)为 BLOCKED，本文任何数字都不是经过验证的估值。**

## 结果

**条件股权剩余价值**：宏观路径与情景参数联合抽样 1,024 次（§1.5）。

| 均值 | 中位数 | P5 | P95 | 股权<0 的概率 |
|---:|---:|---:|---:|---:|
| 252.85 | 184.49 | −103.42 | 904.48 | 25.6% |

**结构情景**（正常宏观周期）：

| 情景 | 第1年收入 | 第5年 | 第10年 | EV | 股权 |
|---|---:|---:|---:|---:|---:|
| 悲观 | 50.67 | 24.88 | 21.68 | −306.95 | −205.14 |
| 基准 | 100.12 | 221.47 | 328.27 | 147.41 | 249.22 |
| 乐观 | 115.69 | 396.70 | 734.42 | 1718.48 | 1820.30 |

**反向 DCF**（`python -m evaluation.reverse_dcf --equity 1200`）：要让股权价值达到约 1.2 万亿美元（IPO 条款对应的市值），单个杠杆需要变成多少。仅作诊断。

| 杠杆（其余保持基准） | 基准 | 所需 |
|---|---:|---:|
| 全部参数朝乐观移动（因子 z） | 0 | 0.75 |
| WACC | 12% | 5.3% |
| 存活公司长期增长 g | 3% | 10.7% |
| 只动份额、需求增长、获客率或用量之一 | — | 达不到（最高约 249–263） |

z = 0.75 时，长期税后利润率为 26.4%，在 18 家云软件公司扣 SBC 后的利润率结果中处于第 89 百分位（§3.2）；基准的 15.75% 处于第 67 百分位。

## 1. 估值模型

```math
V^{(\ell)}=\sum_{t=1}^{10}\frac{FCF^{(\ell)}_t}{(1+W)^t}+\sum_{t=11}^{\infty}\frac{\mathbb E[FCF_t\mid R^{(\ell)}_{10}]}{(1+W)^t}+Cash-Debt,\qquad \widehat V=\frac1L\sum_{\ell=1}^{L}V^{(\ell)}
```

| 符号 | 含义 | 章节 |
|---|---|---|
| $V^{(\ell)}$ | 第 $\ell$ 次抽样（宏观路径和参数）的股权剩余价值 | §1.5 |
| $FCF_t$ | 第1–10年自由现金流 | §1.2 |
| $R_t$ | 收入 | §1.1 |
| $\mathbb E[FCF_t\mid R_{10}]$ | 生命周期延续阶段的期望现金流 | §1.3 |
| $W$ | 折现率（WACC） | §2 |
| $Cash-Debt$ | 备考资产负债调整 | §1.4 |
| $L$ | 抽样次数，1,024 | |

### 1.1 收入

```math
R_t=s_t\,\mathcal R(L_t+T_t+S_t)+B^{\mathrm{pers}}_t,\qquad s_t=\min\Big(1,\frac{C_t}{\mathcal R(L_t+T_t+S_t)}\Big),\qquad \mathcal R(X)=\sum_{i,d,h,v}X_{idhv}\,r_v
```

| 符号 | 含义 |
|---|---|
| $L_t,T_t,S_t$ | 正式 API、试点、企业席位三类账单张量（§1.1.2） |
| $r_v$ | 供应商状态 $v$ 下 Claude 获得的收入比例：$r=(1,0.6,0,0,0,0,0)$ |
| $C_t$ | 企业需求上限（§1.1.5） |
| $s_t$ | 上限缩放系数，同时作用于三个张量 |
| $B^{\mathrm{pers}}_t$ | 个人订阅收入（§1.1.6） |

#### 1.1.1 起点

```math
\omega=\frac{C_{9m}}{R_{9m}}=\frac{26.300}{33.242}=79.12\%,\qquad A_0=R_0\,\omega=64.085,\qquad B_0=R_0(1-\omega)=16.915
```

$R_0$ = 81，为10月年化收入。$A_0$ 为用量（API）收入，$B_0$ 为订阅收入，其中假设50%为个人订阅。把前9个月的结构套用到10月只是近似。来源：[S-1](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074338/anthropicpbc-sx1ax3.htm)、[年化收入披露](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074628/anthropicpbc-fwpjapanprospa.htm)。

#### 1.1.2 客户状态张量

```math
X_t=\mathcal K_{Z_t}\big(\mathcal G_t(X_{t-1})\,M_{Z_t}\big)+A_t,\qquad X\in\mathbb R^{8\times3\times3\times7}
```

| 符号 | 含义 |
|---|---|
| $X_{idhv}$ | 按生命周期 $i$（种子第0–4+年、成长、中小、大型）、停留期 $d$（0/1/2+）、财务健康 $h$、供应商 $v$ 划分的账单量 |
| $Z_t$ | 宏观周期：寒冬、正常、繁荣（§1.1.2.3） |
| $M_{Z}$ | 供应商转移矩阵（§1.1.2.4） |
| $\mathcal K_Z$ | 生命周期与健康转移核（次随机，剩余部分为关闭）（§1.1.2.1） |
| $\mathcal G_t$ | 增长算子（§1.1.3） |
| $A_t$ | 新增账单（§1.1.4） |

##### 1.1.2.1 生命周期转移核

```math
g_k=\frac{F_k-F_{k-1}}{U_{k-1}},\qquad U_k=U_{k-1}(1-g_k-b_k-h_k),\qquad h^{\mathrm{eff}}_{i}=\min\big(0.95,\;h_i\,m^{Z}_{\mathrm{death}}\,m^{H}_{\mathrm{death}}\big)
```

| 符号 | 取值 / 含义 |
|---|---|
| $F_k$ | 种子轮后 $k$ 年内拿到 A 轮的累计比例：10/22/31/36%（基准） |
| $g_k,b_k,h_k$ | 种子期各年的晋级、自力更生、关闭风险 |
| $h_i$ | 各组年关闭率：早期 15.03%、成长 8.06%、中小 7.27%、大型 0.132%（BLS 机构数据；大型为困境代理） |
| $m^{Z}_{\mathrm{death}}$ | 寒冬/正常/繁荣：1.5 / 1 / 0.75 |
| $m^{H}_{\mathrm{death}}$ | 困境/有融资/自给：1.6 / 1 / 0.55 |
| 晋级 | 乘以 $m^Z_{\mathrm{grow}}$ = 0.65 / 1 / 1.25；停留期乘数 0.55 / 1 / 1.20；升级支出 ×1.35，降级 ×0.75 |

##### 1.1.2.2 财务健康隐状态

```math
\pi_{0,h\mid y}=\frac{\pi_{0,h}P(y\mid h)}{\sum_k\pi_{0,k}P(y\mid k)},\qquad P(y=1\mid h)=(0.15,\,0.75,\,0.25)
```

$y$ 表示近期是否观测到融资。正常周期下的转移行为 (.67, .23, .10)、(.18, .62, .20)、(.04, .10, .86)；寒冬时向困境倾斜，繁荣时反之。健康状态同时把支出乘以 0.75 / 1 / 1.10。

##### 1.1.2.3 宏观周期

```math
P_Z=\begin{pmatrix}0.60&0.35&0.05\\0.18&0.67&0.15\\0.08&0.42&0.50\end{pmatrix}\quad(\text{winter, normal, boom})
```

##### 1.1.2.4 供应商转移

```math
M_{i\to w}=\begin{cases}c\,\delta_w & w\in\{\mathrm{OpenAI,Google,self,other,none}\}\\(1-c)\,\sigma & \text{single}\leftrightarrow\text{multi}\\(1-c)(1-\sigma)&\text{stay}\end{cases},\qquad c=\Big(1-\frac{s_g}{1-h_g}\Big)m^Z_c
```

| 符号 | 取值 / 含义 |
|---|---|
| $s_g$ | 各组年收入留存率：69.0 / 78.7 / 82.6 / 92.3% |
| $\delta$ | 流失去向比例：.35 / .25 / .15 / .10 / .15 |
| $\sigma$ | 单一↔多供应商切换概率：0.12（单→多）、0.04（多→单） |
| $m^Z_c$ | 寒冬 1.3，繁荣 0.85 |
| 回流 | 每年从竞争对手回流 0.06、从未购买状态回流 0.035，再乘以 $m^Z_{\mathrm{grow}}$ |

#### 1.1.3 增长算子

```math
d_t=\max\Big(0,1-\frac{t-1}{7}\Big),\qquad \mu_t=[1-(1-p)d_t]\,[1+(q-1)d_t],\qquad \alpha_t=0.1+0.5\,d_t
```

```math
L_t=\mathcal K\big([(L_{t-1}+\phi\,\rho\,T_{t-1})\,F_t\,\mu_t\,H]\,M\big)+(1-\alpha_t)A_t,\qquad T_t=\alpha_tA_t,\qquad S_t=\mathcal K\big([S_{t-1}F_t(1+b\,d_t)H]\,M\big)+A^{\mathrm{seat}}_t
```

| 符号 | 含义（基准） |
|---|---|
| $d_t$ | 增长衰减（§3.3 检验了这一形状） |
| $p,q$ | 初始价格、用量乘数：0.78、1.65 |
| $\phi,\rho$ | 试点成功率、推广倍数：0.35、3 |
| $F_t$ | 早期和成长期企业的融资乘数：$1+(f-1)d_t$ |
| $H$ | 健康状态支出乘数 |
| $b$ | 订阅增长：12% |

#### 1.1.4 新客户

```math
J_t=x_{Z_t}\big[n\,d_t\,\mathcal R(X_{t-1})+\eta(1-d_t)\,\mathcal L(X_{t-1})\big],\qquad \mathcal L(X)=\sum X_{idhv}r_v(1-s_i),\qquad J^{\mathrm{birth}}_t=\min(0.2J_t,\;\mathrm{Budget}_t)
```

$n$ = 0.20 为获客率，$\eta$ = 1 为成熟期补充系数，$x_Z$ 为宏观销售乘数。Budget = 美国种子轮 5,049 笔 × 全球系数 2 × 去重 0.75 × 捕获 0.25 × 平均融资额的 5%，每年 0.418。

#### 1.1.5 企业需求上限

```math
C_t=c_t\sum_i D_{i,t},\qquad D_{i,t}=D_{i,t-1}\big[1+0.03+(m\,g_i-0.03)\max\Big(0,1-\frac{\max(0,t-2)}{8}\Big)\big],\qquad c_t=c_0+(c_{10}-c_0)\min(t/10,1)
```

| 符号 | 含义 |
|---|---|
| $D_{i,0}$ | Menlo 2026 年部署支出 176.8 × IDC 行业权重 $w_i$ |
| $g_i$ | IDC 2024–28 年行业复合增长率；$m$ = 0.7 / 1 / 1.5 |
| $c_0$ | $(81-B_0/2)/176.8$ = 41%，观测到的起始份额 |
| $c_{10}$ | 悲观 15%，基准保持 $c_0$，乐观 50% |

来源：[IDC](https://info.idc.com/rs/081-ATC-910/images/DA-Market-Primer-AI-and-GenAI.pdf)、[Menlo 2026](https://menlovc.com/perspective/2026-the-state-of-enterprise-ai/)。

#### 1.1.6 个人订阅

```math
B^{\mathrm{pers}}_t=\min\Big(B^{\mathrm{raw}}_t\frac{1-\kappa e_t}{1-\kappa e_0},\;R_C+\max(0,B^{\mathrm{pers}}_0-R_C)\max(0,1-t/5)\Big),\qquad R_C=12\,N_N\,k\,F_C
```

| 符号 | 含义 |
|---|---|
| $\kappa$ | 企业版对个人订阅的替代：.8 / .5 / .2 |
| $e_t$ | 企业覆盖率，从 0.4 线性变到 0.8 / 0.7 / 0.6 |
| $N_N$ | Netflix 付费账户数，0.325B |
| $k$ | Claude 与 Netflix 账户数之比：5 / 15 / 30% |
| $F_C$ | 按地区加权的价格，每月 13.53 美元 |

来源：[Netflix 10-K](https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm)。

### 1.2 自由现金流（第1–10年）

```math
Y_t=R_t-\max\big(K^{\mathrm{floor}}_t,\;c_tR_t\big)-(o_t+x_t)R_t,\qquad FCF_t=Y_t-0.25\max(Y_t,0)
```

#### 1.2.1 成本路径

```math
\theta_t=\theta^\ast+(\theta_0-\theta^\ast)\,2^{-t/H},\qquad \theta=(c,o,x),\qquad H=3
```

$\theta_0$ = (56.6%, 47.2%, 2.8%) 为前9个月已披露的算力、其他费用和资本开支比率；$\theta^\ast$ 为情景的长期值（基准 48%, 25%, 6%）。$H$ = 3 年是 18 家云软件公司利润率路径的开发阶段估计（§3.2）。`cost_half_life=None` 表示第1年直接采用 $\theta^\ast$。

#### 1.2.2 算力承诺

```math
K^{\mathrm{floor}}_1=70.7,\qquad K^{\mathrm{floor}}_{2..4}=\frac{451.6-70.7}{3},\qquad K^{\mathrm{floor}}_{5..19}=\frac{900.9-451.6}{15},\qquad K^{\mathrm{floor}}_{20+}=0
```

承诺是现金支出下限，不产生收入。trace 中输出 `commitment_implied_revenue` = $K/c$ 和 `idle_commitment_cost`；基准第1–4年闲置成本为 15.8 / 60.7 / 46.9 / 31.1。

### 1.3 延续价值（第10年之后）

```math
a_{10}=(R_{10},0,0,0),\qquad a_t=a_{t-1}A,\qquad A=P\,\mathrm{diag}\big(k(1+g),\,0.85k,\,1.08k(1+g),\,0\big)
```

```math
\mathbb E[FCF_t]=a_t\,\mu-S_t\max\Big(0,\;K^{\mathrm{floor}}_t-\frac{c\,\mathbf 1^\top a_t}{S_t}\Big),\qquad \sum_{t>30}\frac{\mathbb E[FCF_t]}{(1+W)^t}=\frac{a_{30}B(I-B)^{-1}\mu}{(1+W)^{30}},\quad B=\frac{A}{1+W}
```

| 符号 | 含义 |
|---|---|
| $a_t$ | 各状态（成熟、衰退、转型、退出）的期望收入 |
| $k$ | 增长缩放系数，使存活公司的长期增长等于 $g$：$\rho\big(P_{1:3,1:3}\,\mathrm{diag}(1+g,\,0.85,\,1.08(1+g))\big)\,k=(1+g)(1-e)$ |
| $g$ | 长期增长：2.5 / 3 / 3.5% |
| $S_t$ | 存活概率；退出后股东不再承担承诺 |
| $\mu$ | 各状态利润率（§1.3.2） |

#### 1.3.1 生命周期链与退出风险

```math
P=\begin{pmatrix}1-e-\delta-u&\delta&u&e\\0.10&0.90-e-u&u&e\\0.40&\delta&0.60-e-\delta&e\\0&0&0&1\end{pmatrix},\qquad e=\big[1-(1-0.08)^{1/5}\big]\,\varsigma
```

$e$ 只计零回收的**困境**退出；被收购时股东会拿到对价（§3.4）。$\varsigma$ 为大公司退市中困境退出的占比：基准 8%（[Daepp 等](https://doi.org/10.1098/rsif.2015.0120)），悲观 50%（互联网泡沫时期破产占全部退出的比例，2/4）。乐观情景的 $e$ 为 0.09%/年，即美国大公司历史上的直接失败率。衰退概率 $\delta$ = .30 / .20 / .10，转型概率 $u$ = .03 / .08 / .15。5年8%退市率的来源：[BCG](https://www.bcg.com/publications/2026/why-do-companies-fail-us-failure-rates)。

#### 1.3.2 各状态利润率

```math
\mu=\Big(m,\;0.2m,\;\min\Big(0.6,\frac{4m}{3}\Big),\;0\Big),\qquad m=(1-c^\ast-o^\ast-x^\ast)(1-0.25)
```

基准 $m$ = 15.75%。悲观情景按自身成本率是亏损的，所以尾部价值为负。

### 1.4 股权调整

```math
Cash-Debt=212.684-110.873
```

备考现金和可转债账面价值仅为示意。更新后的调整数（232.351 − 109.742）会增加 20.80。稀释和最终资本结构尚未确定。

### 1.5 不确定性

```math
Z_{t}\sim P_Z,\qquad z\sim\mathrm{Tri}(-1,0,1),\qquad \theta(z)=\theta_{\mathrm{base}}+|z|\,(\theta_{\mathrm{side}(z)}-\theta_{\mathrm{base}})
```

用一个共同因子让所有情景参数同时朝悲观（$z<0$）或乐观（$z>0$）移动。这是一条很宽的同向压力带，不是估计出来的后验分布。只抽宏观路径时，均值为 199.72，P5–P95 为 109.24–262.33。

## 2. 情景参数（假设）

| 参数 | 悲观 | 基准 | 乐观 |
|---|---:|---:|---:|
| 早期 / 成长 / 中小 / 大型权重 | 30/30/25/15% | 15/25/30/30% | 5/15/30/50% |
| 试点比例 | 25% | 30% | 20% |
| 试点成功率 / 推广倍数 | .20 / 2 | .35 / 3 | .50 / 4 |
| 初始用量 / 价格 | 1.45 / .65 | 1.65 / .78 | 1.85 / .88 |
| 获客率 / 补充系数 | .10 / .50 | .20 / 1 | .30 / 1.25 |
| 订阅增长 | 3% | 12% | 22% |
| 长期算力 / 其他 / 资本开支 | .65 / .35 / .06 | .48 / .25 / .06 | .35 / .20 / .05 |
| 第10年份额 $c_{10}$ | 15% | 41%（保持） | 50% |
| 困境退出 $e$ / 衰退 / 转型 | .00827 / .30 / .03 | .00132 / .20 / .08 | .0009 / .10 / .15 |
| 长期增长 $g$ | 2.5% | 3% | 3.5% |
| WACC | 15% | 12% | 10% |

## 3. 证据与验证

### 3.0 数据来源核对

§3.2–3.4 使用的每个 SEC 数字都有两个来源：原始时点的 XBRL 数据，以及申报原文中印出的数字。共 41 份申报、205 个数，全部完全一致（[核对记录](data/sec_reconciliation.csv)；其中 34 个按百万美元披露，只能核对到这一精度）。每笔收购都有两个独立来源（[事件数据](data/stage4_exit_events.csv)），只有 NetSuite 的股权价值仍依赖单一来源。任何数字未经核对，测试都会失败。仓库原有数据也按同样方法逐条核对（[核对记录](data/legacy_reconciliation.csv)）：295 个 SEC 数字全部与申报原文一致；PayPal 现金有误（13.002→13.083），云计算样本的现金口径统一为现金加短期投资，8 个失效链接已替换。非 SEC 来源：市值及大部分锚点数据一致；IDC 分行业数据、JPM/ITU 以及 Cisco/CMGI/VeriSign 1998-99 年数据仍待核。

### 3.1 发布门禁

`python -m evaluation.validation_gate --audit` → **BLOCKED**。发布条件：至少 10 家未暴露的公司、覆盖 2 个技术周期，五年股权 WAPE ≤ 30%，偏差绝对值 ≤ 15%，同时打败"市值不变"和"市销率不变"两个基准，并具备完整公司画像、冻结的预测和独立审核人。[收购终点规则](evaluation/acquisition_endpoint_policy.md)已于 2026-11-19 **获批**并由门禁执行：被收购的公司以成交时股东获得的股权价值为标签，与匹配年限 $k=\max(1,\mathrm{round}(\tau))$ 下的模型股权价值比较，从不按零计。

### 3.2 利润率路径：第四阶段测试（已评分一次）

```math
m=\frac{CFO-\mathrm{capex}-\mathrm{cap.\ software}}{\mathrm{revenue}}
```

预测在打开标签前已预注册并冻结（[预注册](evaluation/stage4_margin_preregistration.md)、[评分](evaluation/stage4_margin_score.json)）。17 家中评分 11 家，另外 6 家被收购，没有标签。

| 模型（MAE，百分点） | 开发集留一 | 第四阶段全部 | 2015 | 2020 |
|---|---:|---:|---:|---:|
| 保持起点利润率 | 9.64 | 23.44 | 18.60 | 25.26 |
| 收敛到 15% | 11.12 | 15.07 | 13.39 | 15.69 |
| 合并均值 | 9.28 | 8.63 | 11.45 | 7.57 |
| 向目标收敛（3年半衰期） | 8.56 | 6.77 | 10.10 | 5.52 |
| **经营杠杆（预注册选中）** | **4.94** | **8.87** | 5.99 | 9.94 |

选中的模型没有打败合并均值，因此未晋级；这份名单现已转入开发集。用全部 18 个观测（`margin_development`）看，5–6 年后扣 SBC 的利润率中位数为 11.1%，P90 为 24.4%。按 3 年半衰期向 18.1%（扣 SBC 口径）收敛，留一 MAE 为 7.26 个百分点，而保持起点利润率为 16.56。建模者对这些公司的后续历史并非不知情。

### 3.3 收入增长持续性（开发阶段）

```math
g_t=g_\infty+(g_0-g_\infty)\,2^{-t/H_g},\qquad g_0=\ln\frac{R_0}{R_{-1}},\qquad \ln\frac{R_h}{R_0}=\sum_{t\le h}g_t
```

| 模型（留一 MAE，对数收入） | 18个观测 |
|---|---:|
| 收入持平 | 1.436 |
| 保持 $g_0$ | 0.660 |
| 引擎式：从 $g_0$ 线性衰减7年 | 0.242 |
| 拟合衰减（$H_g$ = 4，$g_\infty$ = 6.5%） | 0.221 |

引擎衰减的形状和拟合衰减差不多好。从 81 出发的基准路径相当于一家 $g_0\approx$ 0.24–0.29 的 SaaS 公司，处于样本第 17–33 百分位。Anthropic 实际的 $g_0\approx$ 2.57，远高于样本最大值 0.63，因此这些证据无法判断起点是否合适。默认值未作修改。

### 3.4 退出（开发阶段）

| 名单（5年） | 家数 | 被收购 | 破产 | 年化收购率 |
|---|---:|---:|---:|---:|
| 云公司 2015 | 10 | 5 | 0 | ≈12% |
| 云公司 2020 | 14 | 1 | 0 | ≈2% |
| 互联网 1999 | 18 | 2 | 2 | — |

被收购的云公司规模为 30–260 亿美元；2015 批次的 5 笔交易成交价为 2015 年 5 月市值的 1.0–2.2 倍（[事件数据](data/stage4_exit_events.csv)）。因此退出风险 $e$ 只计困境退出（§1.3.1）。

### 3.5 已暴露云公司的五年股权回测（诊断）

Bessemer 2020 年的 5 家公司，以 FY2020 数据为输入，比较 2025 年底市值。利润率向排除自身后拟合的 $m^\ast$ 收敛（§3.2）。

| 指标 | 模型 | 市值不变 | 市销率不变 |
|---|---:|---:|---:|
| 股权 WAPE | 71.17% | 58.82% | 124.89% |
| 股权偏差 | −49.37% | +17.73% | +124.89% |
| 股权 Spearman | −0.3 | −0.6 | −0.6 |
| 收入 / FCF WAPE | 16.25% / 37.91% | — | — |
| 收入 / FCF Spearman | 0.9 / 0.7 | — | — |

模型对基本面排序准确，对市值排序不准；股权误差主要来自估值倍数的分化（2025 年 FCF 的 10–104 倍）。其他版本：保持利润率 69.28%，旧的统一 15% 利润率 77.40%，WACC 8% 时 61.55%。

### 3.6 早期实验（均为回顾性，均未晋级）

| 实验 | 结果 | 脚本 |
|---|---|---|
| 1999 年前十大公司 FY2000 即时预测 | MAPE 21.54%（不变基准 50.23%） | `company_oos` |
| FY2001–04 固定衰减 | MAPE 304.61%，弃用 | `company_oos` |
| 五年饱和模型，留一公司 | WAPE 41.08%（不变基准 61.19%） | `five_year` |
| 1999 年外部队列 | 饱和模型 WAPE 60.21%（不变基准 69.97%） | `external_validation` |
| 财务因子 / 协方差处理 | 外部无改善 | `covariance_factors`、`structural_factors` |
| 2020 云公司收入，冻结的规模组合模型 | WAPE 16.25%（不变基准 50.81%） | `cloud_cycle` |
| 联合引擎聚合约束 | 股权 WAPE 86.19% | `joint_model_audit` |
| 股权损失训练迁移 | 88.48 / 61.40 / 65.63%（不变基准 58.82%） | `equity_training` |
| 互联网公司竞争退出 | 独立 / 破产 / 合并 74 / 13 / 13% | `competing_risk` |

### 3.7 敏感性（基准，正常周期）

| 版本 | 股权 |
|---|---:|
| 基准 | 249.22 |
| 去掉财务健康隐状态 | 152.68 |
| 去掉额外停留期机制 | 252.08 |
| 去掉供应商转移 | 204.25 |
| 全部关闭（开放生命周期） | 123.62 |
| 恒定寒冬 / 繁荣 | 54.35 / 266.22 |
| 成本率第1年直接到长期值 | 322.58 |
| 1,024 条路径均值，调整后过渡：原始 / 固定披露算力率 / 两项比率均固定 | 220.52 / 135.26 / −153.05 |

## 4. 复现

```bash
pip install numpy scipy
python -m unittest discover -s evaluation -p 'test_*.py'   # 129 项测试
python -m evaluation.validation_gate --audit
python -m models.joint_customer_states
python -m evaluation.reverse_dcf --equity 1200
python -m evaluation.margin_path --verify
python -m evaluation.margin_development
python -m evaluation.growth_persistence
python -m evaluation.saas_exit
python -m evaluation.cloud_equity
```

数据定义：[data/README.md](data/README.md)。研究规范：[MODEL_VALIDATION_PROTOCOL.md](MODEL_VALIDATION_PROTOCOL.md)、[AGENTS.md](AGENTS.md)。
