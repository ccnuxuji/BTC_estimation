import streamlit as st
from btc_mining_calculator import BTCMiningCalculator
import time
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# 定义常见矿机型号及其参数
MINER_MODELS = {
    "Custom": {"hashrate": 200.0, "power": 3500.0, "cost": 4000.0, "efficiency": 17.50, "cost_per_th": 20.00},
    "Antminer S23 Hydro": {"hashrate": 580.0, "power": 5510.0, "cost": 14790.0, "efficiency": 9.50, "cost_per_th": 25.50},
    "Antminer S21 XP Hydro": {"hashrate": 473.0, "power": 5676.0, "cost": 10170.0, "efficiency": 12.00, "cost_per_th": 21.50},
    "Antminer S21 XP lmm.": {"hashrate": 300.0, "power": 4050.0, "cost": 7368.0, "efficiency": 13.50, "cost_per_th": 24.56},
    "Antminer S21 pro": {"hashrate": 234.0, "power": 3510.0, "cost": 3744.0, "efficiency": 15.00, "cost_per_th": 16.00},
    "Antminer S21+": {"hashrate": 216.0, "power": 3564.0, "cost": 3240.0, "efficiency": 16.50, "cost_per_th": 15.00},
    "Antminer S21 lmm.": {"hashrate": 215.0, "power": 3440.0, "cost": 3333.0, "efficiency": 16.00, "cost_per_th": 15.50},
    "Antminer S21+ Hydro": {"hashrate": 358.0, "power": 5370.0, "cost": 5370.0, "efficiency": 15.00, "cost_per_th": 15.00},
    "Antminer S19 XP+ Hyd.": {"hashrate": 279.0, "power": 5301.0, "cost": 2790.0, "efficiency": 19.01, "cost_per_th": 10.00},
    "Antminer S19k Pro": {"hashrate": 120.0, "power": 2760.0, "cost": 840.0, "efficiency": 23.00, "cost_per_th": 7.00},
    "Teraflux AH3880": {"hashrate": 450.0, "power": 6525.0, "cost": 4550.0, "efficiency": 14.50, "cost_per_th": 10.11},
    "SEALMINER A2 Pro Hyd": {"hashrate": 500.0, "power": 7450.0, "cost": 7500.0, "efficiency": 14.90, "cost_per_th": 15.00},
    "SEALMINER A2 Pro Air": {"hashrate": 255.0, "power": 3790.0, "cost": 4100.0, "efficiency": 14.86, "cost_per_th": 16.08},
    "Avalon Q": {"hashrate": 90.0, "power": 1674.0, "cost": 1888.0, "efficiency": 18.60, "cost_per_th": 20.98},
    "Whatsminer M50S": {"hashrate": 126.0, "power": 3348.0, "cost": 1500.0, "efficiency": 26.57, "cost_per_th": 11.90},
    "Avalon A1566I-261T": {"hashrate": 261.0, "power": 4959.0, "cost": 3367.0, "efficiency": 19.00, "cost_per_th": 12.90}
}

def get_maintenance_coefficient(efficiency):
    """
    根据矿机效率返回维护成本调整系数
    效率越低（数值越大），维护系数越高
    """
    if efficiency <= 15.0:
        return 1.0  # 高效机型
    elif efficiency <= 20.0:
        return 1.3  # 中效机型
    else:
        return 1.6  # 低效机型

def calculate_adjusted_maintenance_cost(hardware_cost, base_percent, efficiency):
    """
    计算调整后的维护成本
    """
    coefficient = get_maintenance_coefficient(efficiency)
    return hardware_cost * (base_percent / 100) * coefficient

# 设置页面配置
st.set_page_config(
    page_title="比特币挖矿收益计算器",
    page_icon="⛏️",
    layout="wide"
)

# 添加标题和说明
st.title("⛏️ 比特币挖矿收益计算器")
st.markdown("""
这个工具可以帮助您计算比特币挖矿的预期收益和投资回报期。
实时获取比特币价格和网络难度数据，为您提供准确的收益预测。
""")

# 添加计算公式说明
st.markdown("### 📝 计算公式说明")
with st.expander("点击查看详细计算公式", expanded=False):
    st.markdown("""
    #### 核心计算公式：
    
    **1. 每日比特币收益计算：**
    ```
    每日BTC收益 = (矿机算力 / 全网算力) × 每日区块产出 × 区块奖励
    ```
    - 矿机算力：您的矿机算力 (TH/s)
    - 全网算力：网络难度 × 2³² / 600 (H/s)
    - 每日区块产出：144个区块 (每10分钟产生一个区块)
    - 区块奖励：当前包含交易费的区块奖励 (BTC)
    
    **2. 每日收入计算：**
    ```
    每日收入 = 每日BTC收益 × (1 - 矿池手续费%) × BTC当前价格
    ```
    
    **3. 每日总成本计算：**
    ```
    每日总成本 = 每日电费 + 每日维护成本 + 每日折旧
    ```
    - 每日电费 = 功耗(kW) × 24小时 × 电费单价($/kWh)
    - 每日维护成本 = 年度维护成本 / 365
    - 每日折旧 = 年度硬件折旧 / 365
    
    **4. 每日净利润计算：**
    ```
    每日净利润 = 每日收入 - 每日总成本
    ```
    
    **5. 回本天数计算：**
    ```
    回本天数 = 硬件成本 / 每日净利润
    ```
   如果每日净利润 ≤ 0，则表示不能盈利
    
    **注意事项：**
    - 所有计算基于当前BTC价格和网络难度
    - 实际收益会因市场波动而变化
    - 未考虑运营风险和其他额外成本
    """)

# 展示矿机参数表
st.markdown("### 📊 Miner Models Comparison")
st.markdown("勾选要进行敏感性分析的矿机型号：")

# 初始化session state用于存储选中的矿机
if 'selected_miners_for_analysis' not in st.session_state:
    st.session_state.selected_miners_for_analysis = ["Antminer S21 pro", "Antminer S21+", "Custom"]  # 默认选择几个

# 创建带有选择列的表格
col_table, col_controls = st.columns([4, 1])

with col_table:
    # 为每个矿机创建选择框
    miner_selection = {}
    for name in MINER_MODELS.keys():
        miner_selection[name] = st.checkbox(
            name, 
            value=name in st.session_state.selected_miners_for_analysis,
            key=f"select_{name}"
        )
    
    # 更新session state
    st.session_state.selected_miners_for_analysis = [name for name, selected in miner_selection.items() if selected]

with col_controls:
    st.markdown("**快速选择：**")
    if st.button("🔘 全选", key="select_all"):
        st.session_state.selected_miners_for_analysis = list(MINER_MODELS.keys())
        st.rerun()
    
    if st.button("🔲 清空", key="clear_all"):
        st.session_state.selected_miners_for_analysis = []
        st.rerun()
    
    if st.button("⚡ 高效型", key="select_efficient"):
        st.session_state.selected_miners_for_analysis = ["Antminer S23 Hydro", "Antminer S21 XP Hydro", "Antminer S21+ Hydro"]
        st.rerun()

# 显示矿机参数对比表
st.markdown("#### 矿机参数对比表")
miner_param_df = []
for name, params in MINER_MODELS.items():
    status = "✅ 已选中" if name in st.session_state.selected_miners_for_analysis else "⬜ 未选中"
    maintenance_coef = get_maintenance_coefficient(params["efficiency"])
    miner_param_df.append({
        "状态": status,
        "Model": name,
        "Hashrate (TH/s)": f"{params['hashrate']:.1f}",
        "Power (W)": f"{params['power']:.0f}",
        "Cost ($)": f"{params['cost']:.0f}",
        "Efficiency (W/TH)": f"{params['efficiency']:.2f}",
        "维护系数": f"{maintenance_coef:.1f}x",
        "Cost per TH ($/TH)": f"{params['cost_per_th']:.2f}"
    })
miner_param_df = pd.DataFrame(miner_param_df)
st.dataframe(
    miner_param_df.style.format(precision=2),
    use_container_width=True,
    hide_index=True
)

# 显示选中矿机统计
selected_count = len(st.session_state.selected_miners_for_analysis)
if selected_count > 0:
    st.success(f"✅ 已选择 {selected_count} 个矿机进行敏感性分析")
else:
    st.warning("⚠️ 请至少选择一个矿机进行分析")

st.markdown("---")

# 创建两列布局
col1, col2 = st.columns(2)

# 输入参数部分
with col1:
    st.subheader("📊 输入参数")
    
    # 把矿机选择移到表单外面
    miner_model = st.selectbox(
        "选择矿机型号",
        options=list(MINER_MODELS.keys()),
        help="选择预设的矿机型号，或选择'自定义'以手动输入参数",
        key='miner_model'
    )
    
    # 根据选择的矿机型号设置其他参数
    if miner_model is None:
        miner_model = "Custom"
    is_custom = miner_model == "Custom"
    selected_miner = MINER_MODELS[miner_model]
    
    with st.form("mining_params"):
        hashrate = st.number_input(
            "算力 (TH/s)",
            min_value=1.0,
            max_value=5000.0,
            value=selected_miner["hashrate"],
            step=1.0,
            help="矿机的算力，单位为TH/s",
            disabled=not is_custom,
            key='hashrate'
        )
        
        power = st.number_input(
            "功耗 (W)",
            min_value=100.0,
            max_value=10000.0,
            value=selected_miner["power"],
            step=100.0,
            help="矿机的功率消耗，单位为瓦特",
            disabled=not is_custom,
            key='power'
        )
        
        hardware_cost = st.number_input(
            "硬件成本 ($)",
            min_value=100.0,
            max_value=100000.0,
            value=selected_miner["cost"],
            step=100.0,
            help="矿机的购买成本，单位为美元",
            disabled=not is_custom,
            key='hardware_cost'
        )

        electricity_cost = st.number_input(
            "电费 ($/kWh)",
            min_value=0.01,
            max_value=1.0,
            value=0.01,
            step=0.01,
            format="%.3f",
            help="每千瓦时的电费成本，单位为美元"
        )

        block_reward = st.number_input(
            "区块奖励 (BTC)",
            min_value=0.0,
            max_value=50.0,
            value=3.16,
            step=0.01,
            format="%.2f",
            help="当前区块奖励，包含交易手续费收益"
        )

        pool_fee = st.number_input(
            "矿池手续费 (%)",
            min_value=0.0,
            max_value=10.0,
            value=2.0,
            step=0.1,
            format="%.1f",
            help="矿池收取的手续费百分比"
        )

        maintenance_cost_percent = st.number_input(
            "基础维护成本比例 (%)",
            min_value=0.0,
            max_value=50.0,
            value=6.0,  # 默认基础维护成本6%
            step=0.5,
            format="%.1f",
            help="基础维护成本占硬件成本的百分比，系统会根据矿机效率自动调整实际维护成本"
        )

        depreciation_percent = st.number_input(
            "年度硬件折旧比例 (%)",
            min_value=0.0,
            max_value=100.0,
            value=20.0,  # 默认20%年折旧率
            step=1.0,
            format="%.1f",
            help="年度硬件折旧占硬件成本的百分比。推荐：3年折旧33%，4年折旧25%，5年折旧20%"
        )
        
        annual_utilization_rate = st.number_input(
            "年利用率 (%)",
            min_value=1.0,
            max_value=100.0,
            value=75.0,  # 风电默认75%利用率
            step=1.0,
            format="%.1f",
            help="矿机实际运行时间占全年的百分比。风力发电建议60-80%，水电85-95%，火电90-95%"
        )
        
        # 计算实际金额并显示
        maintenance_coefficient = get_maintenance_coefficient(selected_miner["efficiency"])
        maintenance_cost = calculate_adjusted_maintenance_cost(hardware_cost, maintenance_cost_percent, selected_miner["efficiency"])
        depreciation = hardware_cost * (depreciation_percent / 100)
        
        # 显示计算后的实际金额
        col_calc1, col_calc2, col_calc3 = st.columns(3)
        with col_calc1:
            st.info(f"💰 年度维护成本: ${maintenance_cost:.0f}")
            st.caption(f"效率系数: {maintenance_coefficient}x (效率: {selected_miner['efficiency']:.1f} W/TH)")
        with col_calc2:
            st.info(f"📉 年度折旧: ${depreciation:.0f}")
        with col_calc3:
            st.info(f"🔋 年利用率: {annual_utilization_rate:.1f}%")
            st.caption("矿机实际运行时间比例")
        
        # 添加年利用率说明
        with st.expander("🔋 年利用率说明", expanded=False):
            st.markdown("""
            **年利用率定义：**
            - 表示矿机在一年中实际运行的时间占比
            - 影响实际收益和电费，但不影响维护成本和折旧
            
            **不同发电方式建议值：**
            - 🌪️ **风力发电**: 60-80% - 受风况影响，间歇性发电
            - 💧 **水力发电**: 85-95% - 相对稳定，季节性变化
            - 🔥 **火力发电**: 90-95% - 最稳定，可持续运行
            - ☀️ **太阳能发电**: 20-30% - 仅白天发电，受天气影响
            
            **计算影响：**
            - 实际收益 = 理论收益 × 利用率
            - 实际电费 = 理论电费 × 利用率
            - 维护成本和折旧不受影响（设备仍需维护和折旧）
            """)
        
        # 添加效率调整系数说明
        with st.expander("⚙️ 维护成本效率调整说明", expanded=False):
            st.markdown("""
            **效率调整系数原理：**
            - 🟢 **高效机型** (≤15 W/TH): 系数 1.0x - 设备先进，故障率低，维护简单
            - 🟡 **中效机型** (15-20 W/TH): 系数 1.3x - 中等效率，维护需求适中  
            - 🔴 **低效机型** (>20 W/TH): 系数 1.6x - 老旧机型，需要更多设备和维护
            
            **调整逻辑：**
            - 低效机型价格便宜，相同投资需购买更多台设备
            - 设备数量多意味着更多的清洁、维修、零件更换工作
            - 老机型故障率高，技术支持成本增加
            - 实际维护成本 = 基础成本 × 效率系数
            """)
        
        # 添加说明
        with st.expander("💡 维护成本 vs 折旧 说明", expanded=False):
            st.markdown("""
            **维护成本**：实际发生的现金支出
            - 包括：零件更换、清洁、维修、技术服务
            - 性质：运营费用，影响现金流
            - 计算：基础比例 × 效率系数 × 硬件成本
            
            **硬件折旧**：资产价值的会计分摊
            - 包括：设备价值随时间递减的部分
            - 性质：非现金成本，反映投资回收
            
            **年利用率**：矿机实际运行时间占比
            - 影响收益和电费计算，不影响维护成本和折旧
            
            **建议设置**：基础维护成本6%，折旧20%，风电利用率75%
            """)
        
        calculate_button = st.form_submit_button("计算收益")

# 如果点击了计算按钮
if calculate_button:
    with st.spinner('正在获取实时数据并计算...'):
        calculator = BTCMiningCalculator()
        result = calculator.calculate_roi(
            hashrate_th=hashrate,
            power_watts=power,
            electricity_cost_kwh=electricity_cost,
            hardware_cost=hardware_cost,
            pool_fee_percent=pool_fee,
            maintenance_cost_yearly=int(maintenance_cost),
            hardware_depreciation_yearly=int(depreciation),
            block_reward=block_reward,
            annual_utilization_rate=annual_utilization_rate
        )
        
        if result:
            # 显示结果
            with col2:
                st.subheader("💰 收益分析结果")
                
                # 创建两列显示市场数据
                market_col1, market_col2, market_col3 = st.columns(3)
                
                with market_col1:
                    st.metric(
                        "BTC当前价格",
                        f"${result['BTC当前价格']:,.2f}"
                    )
                
                with market_col2:
                    st.metric(
                        "当前网络难度",
                        f"{result['网络难度']:,.2e}"
                    )
                
                with market_col3:
                    st.metric(
                        "年利用率",
                        f"{result['年利用率']:.1f}%"
                    )
                
                # 创建三列显示每日数据
                daily_col1, daily_col2, daily_col3 = st.columns(3)
                
                with daily_col1:
                    st.metric(
                        "每日BTC收益(实际)",
                        f"{result['每日BTC收益(含矿池费)']:.2e} BTC",
                        delta=f"满载: {result['每日BTC收益(满载)']:.2e} BTC"
                    )
                
                with daily_col2:
                    st.metric(
                        "每日收入",
                        f"${result['每日收入(USD)']:,.2f}"
                    )
                
                with daily_col3:
                    st.metric(
                        "每日总成本",
                        f"${result['每日总成本(USD)']:,.2f}"
                    )
                
                # 创建成本明细
                st.subheader("💸 成本明细")
                cost_col1, cost_col2, cost_col3 = st.columns(3)
                
                with cost_col1:
                    st.metric(
                        "每日电费(实际)",
                        f"${result['每日电费(USD)']:,.2f}",
                        delta=f"满载: ${result['每日电费(满载)']:,.2f}"
                    )
                
                with cost_col2:
                    st.metric(
                        "每日维护成本",
                        f"${result['每日维护成本(USD)']:,.2f}"
                    )
                
                with cost_col3:
                    st.metric(
                        "每日折旧",
                        f"${result['每日折旧(USD)']:,.2f}"
                    )
                
                # 创建三列显示利润数据
                st.subheader("📈 利润分析")
                profit_col1, profit_col2, profit_col3 = st.columns(3)
                
                with profit_col1:
                    st.metric(
                        "每日净利润",
                        f"${result['每日净利润(USD)']:,.2f}"
                    )
                
                with profit_col2:
                    st.metric(
                        "月度净利润",
                        f"${result['月度净利润(USD)']:,.2f}"
                    )
                
                with profit_col3:
                    st.metric(
                        "年度净利润",
                        f"${result['年度净利润(USD)']:,.2f}"
                    )
                
                # ROI分析
                st.subheader("📊 投资回报分析")
                roi_days = result['预计回本天数']
                if roi_days != float('inf'):
                    st.success(f"预计回本天数: {roi_days:.1f}天 (约{roi_days/365:.1f}年)")
                    
                    # 添加进度条
                    yearly_roi = (365 / roi_days) * 100 if roi_days > 0 else 0
                    st.progress(min(yearly_roi, 100) / 100)
                    st.text(f"年化回报率: {yearly_roi:.1f}%")
                else:
                    st.error("⚠️ 警告：当前配置下无法盈利！")
                    st.text("建议：降低成本或选择更高效的矿机")

            # 选中矿机对比分析
            st.markdown("---")
            st.subheader("🔍 选中矿机对比分析")
            
            if st.session_state.selected_miners_for_analysis:
                st.markdown(f"基于当前参数设置，对比 {len(st.session_state.selected_miners_for_analysis)} 个选中矿机的收益表现：")
                
                # 计算所有选中矿机的数据
                comparison_data = []
                for miner_name in st.session_state.selected_miners_for_analysis:
                    miner_specs = MINER_MODELS[miner_name]
                    
                    # 计算该矿机的维护成本和折旧
                    miner_maintenance_cost = calculate_adjusted_maintenance_cost(miner_specs["cost"], maintenance_cost_percent, miner_specs["efficiency"])
                    miner_depreciation = miner_specs["cost"] * (depreciation_percent / 100)
                    
                    # 计算收益
                    miner_result = calculator.calculate_roi(
                        hashrate_th=miner_specs["hashrate"],
                        power_watts=miner_specs["power"],
                        electricity_cost_kwh=electricity_cost,
                        hardware_cost=miner_specs["cost"],
                        pool_fee_percent=pool_fee,
                        maintenance_cost_yearly=int(miner_maintenance_cost),
                        hardware_depreciation_yearly=int(miner_depreciation),
                        block_reward=block_reward,
                        annual_utilization_rate=annual_utilization_rate,
                        use_cache=True
                    )
                    
                    if miner_result:
                        roi_days = miner_result['预计回本天数']
                        annual_return = (365 / roi_days) * 100 if roi_days != float('inf') and roi_days > 0 else 0
                        maintenance_coef = get_maintenance_coefficient(miner_specs["efficiency"])
                        
                        comparison_data.append({
                            "矿机型号": miner_name,
                            "算力 (TH/s)": f"{miner_specs['hashrate']:.1f}",
                            "功耗 (W)": f"{miner_specs['power']:.0f}",
                            "效率 (W/TH)": f"{miner_specs['efficiency']:.1f}",
                            "维护系数": f"{maintenance_coef:.1f}x",
                            "硬件成本 ($)": f"{miner_specs['cost']:,.0f}",
                            "每日收入 ($)": f"{miner_result['每日收入(USD)']:,.2f}",
                            "每日成本 ($)": f"{miner_result['每日总成本(USD)']:,.2f}",
                            "每日净利润 ($)": f"{miner_result['每日净利润(USD)']:,.2f}",
                            "月度净利润 ($)": f"{miner_result['月度净利润(USD)']:,.2f}",
                            "年度净利润 ($)": f"{miner_result['年度净利润(USD)']:,.0f}",
                            "回本天数": f"{roi_days:.1f}" if roi_days != float('inf') else "无法回本",
                            "年化回报率 (%)": f"{annual_return:.1f}%"
                        })
                
                if comparison_data:
                    comparison_df = pd.DataFrame(comparison_data)
                    st.dataframe(comparison_df, use_container_width=True, hide_index=True)
                    
                    # 添加最佳表现统计
                    st.markdown("#### 🏆 最佳表现矿机")
                    
                    # 找出各项指标的最佳矿机
                    numeric_data = []
                    for data in comparison_data:
                        numeric_data.append({
                            "矿机型号": data["矿机型号"],
                            "每日净利润": float(data["每日净利润 ($)"].replace('$', '').replace(',', '')),
                            "年度净利润": float(data["年度净利润 ($)"].replace('$', '').replace(',', '')),
                            "回本天数": float(data["回本天数"]) if data["回本天数"] != "无法回本" else float('inf'),
                            "年化回报率": float(data["年化回报率 (%)"].replace('%', ''))
                        })
                    
                    if numeric_data:
                        best_daily_profit = max(numeric_data, key=lambda x: x["每日净利润"])
                        best_annual_profit = max(numeric_data, key=lambda x: x["年度净利润"])
                        best_roi = min([x for x in numeric_data if x["回本天数"] != float('inf')], 
                                      key=lambda x: x["回本天数"], default=None)
                        best_return_rate = max(numeric_data, key=lambda x: x["年化回报率"])
                        
                        col_best1, col_best2, col_best3, col_best4 = st.columns(4)
                        
                        with col_best1:
                            st.metric(
                                "最高日净利润",
                                f"${best_daily_profit['每日净利润']:,.2f}",
                                delta=best_daily_profit['矿机型号']
                            )
                        
                        with col_best2:
                            st.metric(
                                "最高年净利润", 
                                f"${best_annual_profit['年度净利润']:,.0f}",
                                delta=best_annual_profit['矿机型号']
                            )
                        
                        with col_best3:
                            if best_roi:
                                st.metric(
                                    "最快回本",
                                    f"{best_roi['回本天数']:.1f}天",
                                    delta=best_roi['矿机型号']
                                )
                            else:
                                st.metric("最快回本", "暂无可盈利矿机", delta="")
                        
                        with col_best4:
                            st.metric(
                                "最高年化回报",
                                f"{best_return_rate['年化回报率']:.1f}%",
                                delta=best_return_rate['矿机型号']
                            )
                
                else:
                    st.warning("⚠️ 无法计算选中矿机的收益数据，请检查网络连接")
            else:
                st.info("💡 请先在上方选择要对比的矿机型号")

            # 电价敏感性分析
            st.markdown("---")
            st.subheader(f"⚡ 电价敏感性分析")
            
            # 检查是否有选中的矿机
            if not st.session_state.selected_miners_for_analysis:
                st.warning("⚠️ 请先在上方选择要分析的矿机型号")
            else:
                st.markdown(f"分析选中的 {len(st.session_state.selected_miners_for_analysis)} 个矿机在不同电价下的收益情况（基于当前BTC价格和难度）")
                
                # 显示选中的矿机列表
                with st.expander("📋 查看选中的矿机", expanded=False):
                    selected_list = "、".join(st.session_state.selected_miners_for_analysis)
                    st.info(f"正在分析：{selected_list}")

                # 创建电价点（0到0.1美元，步长0.01）
                electricity_prices = [round(i/100, 3) for i in range(11)]  # [0.00, 0.01, 0.02, ..., 0.10]

                # 创建选中矿机的结果数据
                all_miners_data = {}
                
                # 只计算选中的矿机型号数据
                for miner_name in st.session_state.selected_miners_for_analysis:
                    miner_specs = MINER_MODELS[miner_name]
                    data = []
                    for price in electricity_prices:
                        # 计算该矿机的维护成本和折旧
                        miner_maintenance_cost = calculate_adjusted_maintenance_cost(miner_specs["cost"], maintenance_cost_percent, miner_specs["efficiency"])
                        miner_depreciation = miner_specs["cost"] * (depreciation_percent / 100)
                        
                        sensitivity_result = calculator.calculate_roi(
                            hashrate_th=miner_specs["hashrate"],
                            power_watts=miner_specs["power"],
                            electricity_cost_kwh=price,
                            hardware_cost=miner_specs["cost"],
                            pool_fee_percent=pool_fee,
                            maintenance_cost_yearly=int(miner_maintenance_cost),
                            hardware_depreciation_yearly=int(miner_depreciation),
                            block_reward=block_reward,
                            annual_utilization_rate=annual_utilization_rate,
                            use_cache=True
                        )
                        if sensitivity_result:
                            data.append({
                                "Electricity Price ($/kWh)": float(price),
                                "Daily Profit ($)": float(sensitivity_result["每日净利润(USD)"]),
                                "Monthly Profit ($)": float(sensitivity_result["月度净利润(USD)"]),
                                "Annual Profit ($)": float(sensitivity_result["年度净利润(USD)"]),
                                "ROI Days": sensitivity_result["预计回本天数"] if sensitivity_result["预计回本天数"] != float('inf') else None
                            })
                    if data:
                        all_miners_data[miner_name] = pd.DataFrame(data)

                if all_miners_data:
                    # --------- 日收益对比图 ---------
                    st.markdown("#### 📈 Profitability Analysis (Daily Profit)")
                    plt.style.use('dark_background')
                    fig, ax = plt.subplots(figsize=(12, 6))  # 调整图表大小
                    colors = ['#00BFFF', '#FF69B4', '#32CD32', '#FFD700', '#FF4500', '#9370DB', '#8B4513', '#20B2AA', '#DC143C', '#4682B4', '#A0522D', '#2E8B57', '#B8860B', '#C71585', '#556B2F', '#8A2BE2']
                    for (miner_name, df), color in zip(all_miners_data.items(), colors*2):
                        ax.plot(df["Electricity Price ($/kWh)"], df["Daily Profit ($)"],
                                marker='o', markersize=5,  # 减小点的大小
                                linestyle='-', linewidth=2,
                                color=color,
                                markerfacecolor=color,
                                markeredgecolor='white',
                                label=miner_name)
                    ax.grid(True, linestyle='--', alpha=0.2)
                    ax.set_title(f"Mining Profitability vs Electricity Price\n({len(st.session_state.selected_miners_for_analysis)} miners selected)", pad=20)
                    ax.set_xlabel("Electricity Price ($/kWh)")
                    ax.set_ylabel("Daily Profit ($)")
                    ax.set_xlim(-0.005, 0.105)
                    all_profits = [df["Daily Profit ($)"].values for df in all_miners_data.values()]
                    min_profit = min([profit.min() for profit in all_profits])
                    max_profit = max([profit.max() for profit in all_profits])
                    y_margin = (max_profit - min_profit) * 0.1
                    ax.set_ylim(min_profit - y_margin, max_profit + y_margin)
                    ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
                    fig.patch.set_alpha(0)
                    ax.patch.set_alpha(0)
                    plt.tight_layout()
                    st.pyplot(fig)
                    plt.close()

                    # --------- 预计回本天数对比图（带数值标注）---------
                    st.markdown("#### 📈 ROI Days Analysis")
                    fig2, ax2 = plt.subplots(figsize=(12, 6))  # 调整图表大小
                    for (miner_name, df), color in zip(all_miners_data.items(), colors*2):
                        # 只画有效的ROI天数（非None且大于0）
                        x = df["Electricity Price ($/kWh)"]
                        y = df["ROI Days"].apply(lambda v: v if v is not None and v > 0 and v < 10000 else None)
                        
                        # 绘制线条和点
                        ax2.plot(x, y,
                                 marker='o', markersize=5,  # 减小点的大小
                                 linestyle='-', linewidth=2,
                                 color=color,
                                 markerfacecolor=color,
                                 markeredgecolor='white',
                                 label=miner_name)
                        
                        # 添加数值标注（减少标注密度）
                        for i, (x_val, y_val) in enumerate(zip(x, y)):
                            if y_val is not None and i % 2 == 0:  # 每隔一个点标注一次，避免过于密集
                                ax2.annotate(f'{y_val:.0f}d', 
                                            (x_val, y_val),
                                            textcoords="offset points",
                                            xytext=(0, 8),  # 减小标注偏移
                                            ha='center',
                                            fontsize=7,  # 减小字体大小
                                            color=color,
                                            alpha=0.8)
                    
                    ax2.grid(True, linestyle='--', alpha=0.2)
                    ax2.set_title(f"ROI Days vs Electricity Price\n({len(st.session_state.selected_miners_for_analysis)} miners selected)", pad=20)
                    ax2.set_xlabel("Electricity Price ($/kWh)")
                    ax2.set_ylabel("ROI Days")
                    ax2.set_xlim(-0.005, 0.105)
                    ax2.set_yscale('log')  # 用对数坐标更直观
                    ax2.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
                    fig2.patch.set_alpha(0)
                    ax2.patch.set_alpha(0)
                    plt.tight_layout()
                    st.pyplot(fig2)
                    plt.close()

                    # --------- 年化回报率对比图 ---------
                    st.markdown("#### 📈 Annual Return Rate Analysis")
                    fig3, ax3 = plt.subplots(figsize=(12, 6))
                    for (miner_name, df), color in zip(all_miners_data.items(), colors*2):
                        # 计算年化回报率
                        x = df["Electricity Price ($/kWh)"]
                        y = df["ROI Days"].apply(lambda v: (365 / v) * 100 if v is not None and v > 0 and v != float('inf') else 0)
                        
                        # 绘制线条和点
                        ax3.plot(x, y,
                                 marker='o', markersize=5,
                                 linestyle='-', linewidth=2,
                                 color=color,
                                 markerfacecolor=color,
                                 markeredgecolor='white',
                                 label=miner_name)
                        
                        # 添加数值标注（减少标注密度）
                        for i, (x_val, y_val) in enumerate(zip(x, y)):
                            if y_val > 0 and i % 2 == 0:  # 只标注有效的回报率
                                ax3.annotate(f'{y_val:.1f}%', 
                                            (x_val, y_val),
                                            textcoords="offset points",
                                            xytext=(0, 8),
                                            ha='center',
                                            fontsize=7,
                                            color=color,
                                            alpha=0.8)
                    
                    ax3.grid(True, linestyle='--', alpha=0.2)
                    ax3.set_title(f"Annual Return Rate vs Electricity Price\n({len(st.session_state.selected_miners_for_analysis)} miners selected)", pad=20)
                    ax3.set_xlabel("Electricity Price ($/kWh)")
                    ax3.set_ylabel("Annual Return Rate (%)")
                    ax3.set_xlim(-0.005, 0.105)
                    ax3.set_ylim(0, None)  # 年化回报率从0开始
                    ax3.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
                    fig3.patch.set_alpha(0)
                    ax3.patch.set_alpha(0)
                    plt.tight_layout()
                    st.pyplot(fig3)
                    plt.close()

                    # --------- 盈亏平衡点 ---------
                    st.markdown("#### 📊 Break-even Analysis")
                    break_even_data = []
                    for miner_name, df in all_miners_data.items():
                        break_even_price = None
                        for i in range(len(df)-1):
                            if df.iloc[i]["Daily Profit ($)"] >= 0 and df.iloc[i+1]["Daily Profit ($)"] < 0:
                                break_even_price = df.iloc[i]["Electricity Price ($/kWh)"]
                                break
                        
                        if break_even_price is not None:
                            break_even_data.append({
                                "Miner Model": miner_name,
                                "Break-even Price ($/kWh)": break_even_price,
                                "Status": f"Break-even at ${break_even_price:.3f}/kWh"
                            })
                            st.info(f"🔵 {miner_name}: Break-even at ${break_even_price:.3f}/kWh")
                        else:
                            break_even_data.append({
                                "Miner Model": miner_name,
                                "Break-even Price ($/kWh)": ">0.1",
                                "Status": "Always profitable in 0-0.1 $/kWh range"
                            })
                            st.success(f"🟢 {miner_name}: Always profitable in the given range")
                    
                    # 显示盈亏平衡点汇总表
                    if break_even_data:
                        st.markdown("##### 盈亏平衡点汇总")
                        break_even_df = pd.DataFrame(break_even_data)
                        st.dataframe(break_even_df, use_container_width=True, hide_index=True)
                
                elif st.session_state.selected_miners_for_analysis:
                    st.error("选中的矿机数据计算失败，请检查网络连接或稍后重试")

        else:
            st.error("无法获取必要的数据，请稍后重试。")

# 添加说明信息
st.markdown("""
---
### 📝 注意事项：
1. 所有计算基于当前比特币价格和网络难度
2. 实际收益可能因市场波动而变化
3. 电价敏感性分析范围为 0-0.1 $/kWh
4. 维护成本按效率自动调整：高效机型1.0x，中效机型1.3x，低效机型1.6x
5. 折旧按硬件成本百分比计算，维护成本考虑设备数量和可靠性
6. 年利用率影响实际收益和电费，但不影响维护成本和折旧
7. 风力发电建议利用率60-80%，水电85-95%，火电90-95%
8. 建议定期重新计算以获取最新结果
9. ROI图中的数值标注显示预计回本天数（d=天）
10. 年化回报率图显示投资年化收益率百分比
""")

# 添加更新时间
st.sidebar.write("最后更新时间:", time.strftime("%Y-%m-%d %H:%M:%S")) 