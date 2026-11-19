# Anthropic 估值研究 — 生命周期 DCF（v2）

[English](README.md) · **简体中文**

研究日期：2026-11-19。除特别注明外，金额单位均为十亿美元。本研究为探索性条件压力测试，并非公允价值目标。

## 估值结果

| 情景 | 第1年收入 | 第5年收入 | 第10年收入 | 前10年现金流现值 | 第11–30年现金流现值 | 企业价值 | 股权剩余价值 |
|---|---:|---:|---:|---:|---:|---:|---:|
| 悲观 | 57.15 | 36.66 | 31.40 | -255.00 | -21.68 | -276.68 | -174.87 |
| 基准 | 105.30 | 202.50 | 221.34 | 45.56 | 33.10 | 78.66 | 180.47 |
| 乐观 | 137.70 | 364.50 | 467.21 | 516.03 | 163.20 | 679.23 | 781.04 |

股权剩余价值为负表示融资困境，并非股价为负。模型尚未纳入融资或重组路径。旧版无约束 Gordon 增长情景的估值为 5,446.15；v2 同时修改收入约束和终值方法，因此差异不能仅归因于 Gordon 模型。所有情景均尚未完成统计校准。

## 数学估值方法

除单位价格外，所有金额变量均以**十亿美元**计。时间 $t$ 以2026年10月年化收入快照为起点，按年递推。标为假设的数值属于情景输入，并非真实观测或实证估计。

### 第1步 — 建立收入基准

**观测输入**

| 输入 | 数值 | 定义 |
|---|---:|---|
| $R_0$ | 81.000 | 10月年化运行收入 |
| $R_{9m}$ | 33.242 | 前9个月实际收入 |
| $C_{9m}$ | 26.300 | 前9个月按用量计费收入 |

**按用量计费收入占比：**

```math
\omega=\frac{C_{9m}}{R_{9m}}=\frac{26.300}{33.242}\approx79.12\%
```

**初始化用量与订阅收入：**

```math
A_0=R_0\omega\approx64.085
```

```math
B_0=R_0(1-\omega)\approx16.915
```

来源：[SEC 招股书](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074338/anthropicpbc-sx1ax3.htm), [10月年化收入披露](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074628/anthropicpbc-fwpjapanprospa.htm). 将历史收入结构用于10月仅为代理假设，而非10月实际收入结构。按用量计费不等同于纯 API 收入，订阅也不等同于纯个人消费收入。

### 第2步 — 自下而上的消费者需求（独立交叉验证）

对国家 $c$、年龄组 $a$ 与家庭收入组 $h$，定义：

```math
R_{\mathrm{consumer},t}
=12\sum_{c,a,h}N_{cah,t}I_{cah,t}U_{cah,t}P_{cah,t}M_{cah,t}F_{cah,t}
```

| 符号 | 定义 |
|---|---|
| $N$ | 人口（十亿人） |
| $I$ | 互联网接入概率 |
| $U$ | 接入互联网后的 AI 使用概率 |
| $P$ | 使用 AI 后的付费转化率 |
| $M$ | Anthropic 在付费用户中的份额 |
| $F$ | 每名付费用户实际月均价格（美元） |

**数据依据：** [Pew 年龄分组调查](https://www.pewresearch.org/chart/majorities-of-adults-under-50-now-use-chatgpt/), [ITU 互联网接入](https://www.itu.int/itu-d/reports/statistics/facts-figures-2025/), [世界银行收入分组](https://databank.worldbank.org/metadataglossary/world-development-indicators/country/HIC).

美国聊天机器人曾使用率不等于全球付费转化率；国家 GNI 分类也不等于家庭收入分层。应排除未开放市场。自下而上模型已实现，但缺少国家级付费需求数据，尚未校准，因此未叠加到年化收入递推中。

#### Netflix 付费账户校准压力测试

Netflix 2025年付费账户突破3.25亿，覆盖接近10亿观众，一个账户平均对应约三名观众。定义 $N_N$ 为付费账户（十亿），$A_N$ 为观众（十亿），$q$ 为每账户观众数，$k$ 为 Claude 个人付费账户相对 Netflix 付费账户的假设比例。以观众为基准的等效转化率是 $k/q$，而不是 $k$。该指标不是实测 AI 转化率。Netflix 同样不在中国大陆运营，但其他市场边界可能不同；不能使用全球人口作为分母。

```math
N_C=N_N k=A_N\frac{k}{q},\qquad q=\frac{A_N}{N_N}\approx3.08
```

```math
F_C=20\sum_r\frac{N_{N,r}}{\sum_j N_{N,j}}\frac{F_{N,r}}{17.20}\approx13.53
```

```math
R_C=12N_CF_C
```

2024年各地区付费账户（百万）及月均账户收入：美加89.625 / $17.20；欧洲中东非洲101.133 / $10.96；拉美53.327 / $8.24；亚太57.541 / $7.29。假设地区账户结构相同，并用区域相对价格指数调整北美20美元的假设价格，得到全球月均13.53美元。这并非 Claude 实际地区客单价。5%、15%、30%均为情景假设，对应 Netflix 观众的约1.63%、4.88%、9.75%。独立 DCF 压力测试在五年内逐渐引入个人收入上限，企业账单不受影响；上方原始估值仍是未加入该约束的基准。生命周期尾部未单独施加个人上限。

| 情景 | k | 个人付费账户（百万） | 年收入上限（十亿美元） | 压力测试企业价值（十亿美元） | 压力测试股权价值（十亿美元） |
|---|---:|---:|---:|---:|---:|
| 悲观 | 5% | 16.25 | 2.64 | -286.94 | -185.13 |
| 基准 | 15% | 48.75 | 7.91 | 78.46 | 180.27 |
| 乐观 | 30% | 97.50 | 15.83 | 679.23 | 781.04 |

[Netflix 2024 SEC 10-K](https://www.sec.gov/Archives/edgar/data/1065280/000106528025000044/nflx-20241231.htm) · [2025 Q4 shareholder letter](https://www.sec.gov/Archives/edgar/data/1065280/000106528026000033/ex991_q425.htm) · [Netflix supported markets](https://help.netflix.com/en/node/14164/).

复现：`python -m models.netflix_benchmark`。


### 第3步 — 自下而上的企业需求（独立交叉验证）

对国家 $c$、行业 $j$ 和企业规模组 $k$：

```math
R_{\mathrm{enterprise},t}
=12\sum_{c,j,k}E_{cjk,t}D_{cjk,t}X_{cjk,t}M_{cjk,t}
```

| 符号 | 定义 |
|---|---|
| $E$ | 员工数（十亿人） |
| $D$ | 采用 AI 的企业员工占比（按员工加权） |
| $X$ | 采用 AI 的企业人均月度平均支出 |
| $M$ | Anthropic 获得的支出份额 |

来源： [Ramp AI Index](https://ramp.com/data/ai-index?stream=top). 没有额外权重数据时，Ramp 企业采用率与支出中位数不能替代员工加权采用率和平均支出。此验证尚未校准，不叠加到预测收入中。

### 第4步 — 按风险分组拆分现有用量收入

```math
S_0=A_0w_S,\qquad L_0=A_0w_L
```

```math
H_0=A_0(1-w_S-w_L)
```

| 符号 | 定义 |
|---|---|
| $S_t$ | 创业公司群组收入 |
| $L_t$ | 试验项目群组收入 |
| $H_t$ | 成熟部署群组收入 |
| $w_S,w_L$ | 假设的初始群组占比 |

基准情景：$w_S=0.40$，$w_L=0.30$。这是未观测的分配假设，不是实际客户结构。

**资本循环诊断（尚不可识别）：**

```math
\phi_{\mathrm{VC}}=\frac{\sum_i R_i f_i}{\sum_i R_i}
```

其中 $R_i$ 为客户贡献收入，$f_i$ 为其风投资金支持比例。账单级资金来源数据缺失；不能直接相乘 Ramp 支出集中度和摩根大通的风投背景企业数量占比。

### 第5步 — 创业公司存活与融资风险

采用恒定风险强度的生存近似：

```math
\lambda=-\frac{\ln s_5}{5}
```

```math
s(t)=e^{-\lambda t}=s_5^{t/5}
```

```math
s_1=0.54^{1/5}\approx0.884
```

基准五年存活率54%取自历史代理数据 [BLS 历史经营单位群组](https://www.bls.gov/spotlight/2024/business-employment-dynamics-twentieth-anniversary/)，不是实测 AI 创业公司存活率。

考虑存活、融资与用量变化后的存量创业公司收入：

```math
S_t^{\mathrm{existing}}
=S_{t-1}s_1F_tK_t
```

```math
F_t=1+(f-1)d_t
```

$f$ 为条件融资／支出乘数，$d_t$ 为下文定义的衰减因子，$K_t$ 为价格、用量和市场份额的共同乘数。

### 第6步 — GTM 转化与项目推广

```math
G(L,p,m,r)=L\left[pm+(1-p)r\right]
```

| 符号 | 定义 |
|---|---|
| $L$ | 现有试验项目收入 |
| $p$ | 成功部署比例（假设按收入加权） |
| $m$ | 成功后支出扩张倍数 |
| $r$ | 失败项目剩余支出 |

当前预测设 $r=0$，将成功项目转入成熟群组：

```math
G_t=p\,m\,L_{t-1}
```

收入持平示例：

```math
G(100,0.25,4,0)=100
```

数据依据： [Gartner 项目放弃率](https://www.gartner.com/en/articles/genai-project-failure), [McKinsey 企业 AI 影响](https://www.mckinsey.com/capabilities/quantumblack/our-insights/the-state-of-ai-2025), [ChartMogul 下游留存](https://chartmogul.com/reports/saas-retention-the-ai-churn-wave/). 项目数量口径的放弃率、EBIT 影响和软件净收入留存率（NRR）衡量不同结果，均不能直接识别收入加权的 $p$。

### 第7步 — Token 定价、竞争与增长衰减

基本恒等式：

```math
R_{\mathrm{token},t}=Q_t P_t M_t
```

$Q_t$ 为 Token 总用量，$P_t$ 为每 Token 实际美元价格，$M_t$ 为统一价格口径下的供应商用量份额。

份额不变时，抵消价格跌幅 $\delta$ 所需的用量增长为：

```math
g_Q=\frac{1}{1-\delta}-1
```

```math
\delta=50\%\quad\Longrightarrow\quad g_Q=100\%
```

预测中的年度乘数逐渐趋近于1：

```math
d_t=\max\left(0,1-\frac{t-1}{7}\right)
```

```math
K_t=\left[1+(v-1)d_t\right]\left[1-(1-q)d_t\right]\left[1-(1-m_s)d_t\right]
```

$v$、$q$、$m_s$ 分别为初始年度用量、价格和市场份额乘数。价格压力参考： [Ramp September 2026](https://ramp.com/data/ai-index-sept-2026).

### 第8步 — 考虑个人与雇主需求重叠的收入递推

```math
J_t=n d_t(S_{t-1}+L_{t-1}+H_{t-1})
```

```math
S_t=S_{t-1}s_1F_tK_t+0.4J_t,\qquad L_t=0.6J_t
```

```math
H_t=(H_{t-1}+pmL_{t-1})K_t
```


用量和订阅属于账单类别，而不是去重用户。将订阅拆为个人与企业账单（初始个人占比假设为50%）。A 表示个人付费，B 表示雇主提供 AI。

```math
\Pr(A\cup B)=\Pr(A)+\Pr(B)-\Pr(A\cap B)
```

```math
\Pr(A)=\Pr(A\mid B)\Pr(B)+\Pr(A\mid B^c)(1-\Pr(B))
```

```math
\kappa=1-\frac{\Pr(A\mid B)}{\Pr(A\mid B^c)},\qquad \Pr(A)=\Pr(A\mid B^c)(1-\kappa\Pr(B))
```


两笔真实独立账单均计入收入，仅调整条件需求。雇主覆盖率从 e0 插值至 e10。个人收入相对基准重叠程度调整；企业订阅按假设增长率 b 独立增长。

```math
e_t=e_0+(e_{10}-e_0)\min(t/10,1)
```

```math
B^{raw}_t=B^{raw}_{t-1}(1+bd_t)
```

```math
B^{personal}_t=B^{raw}_t\frac{1-\kappa e_t}{1-\kappa e_0}
```

```math
B^{enterprise}_t=B^{enterprise}_{t-1}(1+bd_t)
```

```math
R_t^{raw}=S_t+L_t+H_t+B^{personal}_t+B^{enterprise}_t
```


设置条件性有效收入上限，约束预测，但它并非实测 TAM：

```math
D_t=81[1+(d_{\max}-1)\min(t/10,1)]
```

```math
R_t=\min(R_t^{raw},D_t)
```


达到上限时，各群组及原始个人订阅累计值按同一比例缩放。收入上限为明确的压力测试输入，不能替代实际国家与行业需求校准。

### 第9步 — 算力承诺与自由现金流

[SEC 招股书](https://www.sec.gov/Archives/edgar/data/2130357/000162828026074338/anthropicpbc-sx1ax3.htm): 总承诺支出900.9，其中未来12个月70.7，2030年底前451.6。近似年度分配与总额一致；实际逐年到期安排未知。

```math
K^{floor}_1=70.7,\qquad K^{floor}_{2:4}=(451.6-70.7)/3
```

```math
K^{floor}_{5:19}=(900.9-451.6)/15,\qquad K^{floor}_{20:30}=0
```

```math
C_t=\max(K^{floor}_t,cR_t),\qquad O_t=oR_t,\qquad X_t=xR_t
```

```math
Y_t=R_t-C_t-O_t-X_t,\qquad FCF_t=Y_t-0.25\max(Y_t,0)
```


采用现金税代理，尚无营运资本预测。承诺支出为成本下限，不重复叠加至可变算力费用。历史经营现金流减固定资产采购为5.644，再减租赁预付款为3.689；两者均非标准化 FCFF。

### 第10步 — 企业生命周期延续价值（替代 Gordon 终值）

#### 为什么替换 Gordon Growth Model？

Gordon 模型假设持续经营的企业，其标准化现金流按固定速率无限期增长：

```math
TV_T=\frac{FCF_T(1+g)}{W-g}
```


若现金流假设成立且折现率大于增长率，该公式数学上有效。但对于面对商品化、价格竞争和商业模式替代的年轻模型供应商，不宜默认使用。Gordon 也允许零或负增长；真正的问题是强制设定一种永久状态。

- [Chan, Karceski and Lakonishok (2003)](https://www.nber.org/papers/w8282) 发现企业长期盈利增长的持续性较弱，可预测性有限。
- [BLS 2013年群组](https://www.bls.gov/opub/ted/2024/34-7-percent-of-business-establishments-born-in-2013-were-still-operating-in-2023.htm): 34.7%的商业经营单位存活十年。
- [BLS 2000年群组](https://www.bls.gov/opub/ted/2026/outlast-state-establishment-survival-rates-from-2000-to-2026.htm): 15.7%存活26年。这些是经营单位，并非匹配的上市科技公司；两项数据均不能直接校准 Anthropic 的退出风险。

行业增长不保证单个企业现金流增长。产业收益可能被客户及竞争者获得。新模型允许衰退、转型和吸收性退出。使用30年有限期限，之后剩余价值为零，是保守截断假设，并非证明公司必然消失。


第10年初始状态为成熟经营。状态顺序：成熟、衰退、转型、退出。退出为吸收状态。年度退出概率 e、衰退概率 d、转型概率 u 均为假设，尚未拟合。

```math
P=\begin{pmatrix}1-e-d-u&d&u&e\\0.10&1-e-0.10-u&u&e\\0.40&d&1-e-0.40-d&e\\0&0&0&1\end{pmatrix}
```

```math
\pi_{10}=(1,0,0,0),\qquad \pi_t=\pi_{t-1}P
```


按状态跟踪概率加权收入，而非仅用概率乘固定收入，从而保留路径依赖增长。

```math
a_{10}=(R_{10},0,0,0),\qquad a_t=a_{t-1}P\,\mathrm{diag}(1,0.85,1.08,0)
```

```math
E[R_t]=\sum_j a_{t,j}
```


各状态假定的标准化税后现金流利润率分别为15%、3%、20%、0%，已经包含普通可变算力、其他费用和资本开支。远期阶段没有新增收入上限。无合同解除的压力测试即使退出仍承担剩余承诺；实际清偿或回收尚未建模。

```math
E[FCF_t]\approx \sum_j a_{t,j}\mu_j-\max(0,K^{floor}_t-cE[R_t])
```


由于凸性，总量承诺缺口是下界，并非精确的期望缺口。

```math
EV_0=\sum_{t=1}^{10}\frac{FCF_t}{(1+W)^t}+\sum_{t=11}^{30}\frac{E[FCF_t]}{(1+W)^t}
```

```math
V_{\mathrm{equity}}=EV_0+212.684-110.873
```


备考现金和可转债账面价值仅为示例；最终资本结构、偿还条款和稀释仍待核对。不假设期末出售价值或第30年后的现金流。退出概率不应与 WACC 中信用风险重复计算。

### 第11步 — 情景模拟

使用固定随机种子的2,000次三角分布抽样，以共同因子在悲观、基准和乐观参数之间插值。股权剩余价值分位数为 -70.70 / 185.39 / 455.97，并非统计置信区间。

## 情景参数

| Input | 悲观 | 基准 | 乐观 |
|---|---:|---:|---:|
| 创业公司／试验项目初始权重 | 55% / 25% | 40% / 30% | 25% / 20% |
| 创业公司五年存活率 | 40% | 54% | 65% |
| 融资乘数 | .70 | .90 | 1.05 |
| GTM 成功率／推广倍数 | .20 / 2 | .35 / 3 | .50 / 4 |
| 初始用量／价格／份额乘数 | 1.45 / .65 / .90 | 1.65 / .78 / .96 | 1.85 / .88 / 1.00 |
| 新增用量收入比例 | 10% | 20% | 30% |
| 订阅增长率 | 3% | 12% | 22% |
| 算力／其他费用／资本开支比例 | .65 / .35 / .06 | .48 / .25 / .06 | .35 / .20 / .05 |
| 第10年收入上限（81的倍数） | 2 | 4 | 8 |
| 初始雇主覆盖率 | 40% | 40% | 40% |
| 第10年雇主覆盖率 | 80% | 70% | 60% |
| 需求替代率 | 80% | 50% | 20% |
| 年度生命周期退出／衰退／转型概率 | 12% / 30% / 3% | 6% / 20% / 8% | 3% / 10% / 15% |
| 折现率 | 15% | 12% | 10% |

这些是情景假设，并非实测值。以到达第10年为条件，第11–30年存活概率为基准29.0%、悲观7.8%、乐观54.4%。

## 复现与验证

```bash
python -m models.valuation
python -m unittest discover -s evaluation -v
```


10项测试通过：数据来源完整性、历史财务核对、BLS 留一群组验证、项目转化、价格用量恒等式、情景排序、可复现性、承诺支出总额、需求重叠与收入上限、生命周期退出。历史代理验证并非已校准的 Anthropic 样本外回测。

- [数据登记表](data/observations.csv)
- [数据定义](data/README.md)
- [模型](models/valuation.py)
- [测试](evaluation/test_models.py)

后续：估计国家与年龄分组付费转化率、雇主需求重叠、客户资金来源、企业预算、可比上市科技公司的生命周期转移概率，以及实际承诺支付计划。在此之前，不声称得到精确内在价值。
