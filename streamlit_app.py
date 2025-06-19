import streamlit as st
from btc_mining_calculator import BTCMiningCalculator
import time
import pandas as pd
import numpy as np
import plotly.express as px
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
    # "Teraflux AH3880": {"hashrate": 450.0, "power": 6525.0, "cost": 10000.0},
    # "SEALMINER A2 Pro Hyd": {"hashrate": 500.0, "power": 7450.0, "cost": 10000.0},
    # "SEALMINER A2 Pro Air": {"hashrate": 255.0, "power": 3790.0, "cost": 10000.0},
    # "Avalon Q": {"hashrate": 90.0, "power": 1674.0, "cost": 10000.0},
    # "Whatsminer M50S": {"hashrate": 126.0, "power": 3348.0, "cost": 2500.0},
    # "Avalon 1366i": {"hashrate": 88.0, "power": 3300.0, "cost": 1800.0},
    # "iPollo B2": {"hashrate": 130.0, "power": 3250.0, "cost": 2300.0}
}

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
miner_param_df = []
for name, params in MINER_MODELS.items():
    miner_param_df.append({
        "Model": name,
        "Hashrate (TH/s)": f"{params['hashrate']:.1f}",
        "Power (W)": f"{params['power']:.0f}",
        "Cost ($)": f"{params['cost']:.0f}",
        "Efficiency (W/TH)": f"{params['efficiency']:.2f}",
        "Cost per TH ($/TH)": f"{params['cost_per_th']:.2f}"
    })
miner_param_df = pd.DataFrame(miner_param_df)
st.dataframe(
    miner_param_df.style.format(precision=2),
    use_container_width=True,
    hide_index=True
)

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

        maintenance_cost = st.number_input(
            "年度维护成本 ($)",
            min_value=0.0,
            max_value=10000.0,
            value=0.0,
            step=100.0,
            help="每年的维护成本，包括维修、清洁等费用"
        )

        depreciation = st.number_input(
            "年度硬件折旧 ($)",
            min_value=0.0,
            max_value=hardware_cost,
            value=hardware_cost * 0.2,  # 默认20%年折旧率
            step=100.0,
            help="每年的硬件折旧成本"
        )
        
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
            maintenance_cost_yearly=maintenance_cost,
            hardware_depreciation_yearly=depreciation,
            block_reward=block_reward
        )
        
        if result:
            # 显示结果
            with col2:
                st.subheader("💰 收益分析结果")
                
                # 创建两列显示市场数据
                market_col1, market_col2 = st.columns(2)
                
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
                
                # 创建三列显示每日数据
                daily_col1, daily_col2, daily_col3 = st.columns(3)
                
                with daily_col1:
                    st.metric(
                        "每日BTC收益(含矿池费)",
                        f"{result['每日BTC收益(含矿池费)']:.2e} BTC"
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
                        "每日电费",
                        f"${result['每日电费(USD)']:,.2f}"
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

            # 电价敏感性分析
            st.markdown("---")
            st.subheader(f"⚡ 电价敏感性分析 - {miner_model}")
            st.markdown("分析当前选择矿机在不同电价下的收益情况（基于当前BTC价格和难度）")

            # 创建电价点（0到0.1美元，步长0.01）
            electricity_prices = [round(i/100, 3) for i in range(11)]  # [0.00, 0.01, 0.02, ..., 0.10]

            # 创建所有矿机的结果数据
            all_miners_data = {}
            
            # 计算所有矿机型号的数据（不再区分用户选择，全部分析）
            for miner_name, miner_specs in MINER_MODELS.items():
                data = []
                for price in electricity_prices:
                    sensitivity_result = calculator.calculate_roi(
                        hashrate_th=miner_specs["hashrate"],
                        power_watts=miner_specs["power"],
                        electricity_cost_kwh=price,
                        hardware_cost=miner_specs["cost"],
                        pool_fee_percent=pool_fee,
                        maintenance_cost_yearly=maintenance_cost,
                        hardware_depreciation_yearly=depreciation,
                        block_reward=block_reward,
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
                fig, ax = plt.subplots(figsize=(8, 5))
                colors = ['#00BFFF', '#FF69B4', '#32CD32', '#FFD700', '#FF4500', '#9370DB', '#8B4513', '#20B2AA', '#DC143C', '#4682B4', '#A0522D', '#2E8B57', '#B8860B', '#C71585', '#556B2F', '#8A2BE2']
                for (miner_name, df), color in zip(all_miners_data.items(), colors*2):
                    ax.plot(df["Electricity Price ($/kWh)"], df["Daily Profit ($)"],
                            marker='o', markersize=6,
                            linestyle='-', linewidth=2,
                            color=color,
                            markerfacecolor=color,
                            markeredgecolor='white',
                            label=miner_name)
                ax.grid(True, linestyle='--', alpha=0.2)
                ax.set_title("Mining Profitability vs Electricity Price", pad=20)
                ax.set_xlabel("Electricity Price ($/kWh)")
                ax.set_ylabel("Daily Profit ($)")
                ax.set_xlim(-0.005, 0.105)
                all_profits = [df["Daily Profit ($)"].values for df in all_miners_data.values()]
                min_profit = min([profit.min() for profit in all_profits])
                max_profit = max([profit.max() for profit in all_profits])
                y_margin = (max_profit - min_profit) * 0.1
                ax.set_ylim(min_profit - y_margin, max_profit + y_margin)
                ax.axhline(y=0, color='red', linestyle='--', alpha=0.5)
                ax.text(0.01, 0, 'Break-even Line', color='red', alpha=0.8)
                ax.legend(bbox_to_anchor=(1.05, 1), loc='upper left', fontsize='small')
                fig.patch.set_alpha(0)
                ax.patch.set_alpha(0)
                plt.tight_layout()
                st.pyplot(fig)
                plt.close()

                # --------- 预计回本天数对比图（带数值标注）---------
                st.markdown("#### 📈 ROI Days Analysis")
                fig2, ax2 = plt.subplots(figsize=(10, 6))
                for (miner_name, df), color in zip(all_miners_data.items(), colors*2):
                    # 只画有效的ROI天数（非None且大于0）
                    x = df["Electricity Price ($/kWh)"]
                    y = df["ROI Days"].apply(lambda v: v if v is not None and v > 0 and v < 10000 else None)
                    
                    # 绘制线条和点
                    ax2.plot(x, y,
                             marker='o', markersize=6,
                             linestyle='-', linewidth=2,
                             color=color,
                             markerfacecolor=color,
                             markeredgecolor='white',
                             label=miner_name)
                    
                    # 添加数值标注
                    for i, (x_val, y_val) in enumerate(zip(x, y)):
                        if y_val is not None and i % 2 == 0:  # 每隔一个点标注一次，避免过于密集
                            ax2.annotate(f'{y_val:.0f}d', 
                                        (x_val, y_val),
                                        textcoords="offset points",
                                        xytext=(0, 10),
                                        ha='center',
                                        fontsize=8,
                                        color=color,
                                        alpha=0.8)
                
                ax2.grid(True, linestyle='--', alpha=0.2)
                ax2.set_title("ROI Days vs Electricity Price (with value annotations)", pad=20)
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

                # --------- 盈亏平衡点 ---------
                st.markdown("#### Break-even Analysis")
                for miner_name, df in all_miners_data.items():
                    break_even_price = None
                    for i in range(len(df)-1):
                        if df.iloc[i]["Daily Profit ($)"] >= 0 and df.iloc[i+1]["Daily Profit ($)"] < 0:
                            break_even_price = df.iloc[i]["Electricity Price ($/kWh)"]
                            break
                    if break_even_price is not None:
                        st.info(f"{miner_name}: Break-even at ${break_even_price:.3f}/kWh")
                    else:
                        st.info(f"{miner_name}: Always profitable in the given range")

        else:
            st.error("无法获取必要的数据，请稍后重试。")

# 添加说明信息
st.markdown("""
---
### 📝 注意事项：
1. 所有计算基于当前比特币价格和网络难度
2. 实际收益可能因市场波动而变化
3. 电价敏感性分析范围为 0-0.1 $/kWh
4. 未考虑其他运维成本变化
5. 建议定期重新计算以获取最新结果
6. ROI图中的数值标注显示预计回本天数（d=天）
""")

# 添加更新时间
st.sidebar.write("最后更新时间:", time.strftime("%Y-%m-%d %H:%M:%S")) 