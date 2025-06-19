import requests
import pandas as pd
from datetime import datetime, timedelta
import time
import json

class BTCMiningCalculator:
    def __init__(self):
        # 主要API
        self.binance_api_url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        # 备用API
        self.coingecko_api_url = "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd"
        self.okx_api_url = "https://www.okx.com/api/v5/market/ticker?instId=BTC-USDT"
        self.difficulty_api_url = "https://blockchain.info/q/getdifficulty"
        self.block_reward = 3.16  # 默认区块奖励
        # 添加缓存
        self._btc_price_cache = None
        self._network_difficulty_cache = None

    def get_btc_price(self, use_cache=False):
        """
        获取当前比特币价格，如果主API失败则尝试备用API
        :param use_cache: 是否使用缓存的价格
        """
        if use_cache and self._btc_price_cache is not None:
            return self._btc_price_cache

        # 尝试Binance API
        try:
            print("\n尝试从Binance获取价格...")
            response = requests.get(self.binance_api_url, timeout=10)
            print(f"Binance API状态码: {response.status_code}")
            print(f"Binance返回内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'price' in data:
                    self._btc_price_cache = float(data['price'])
                    return self._btc_price_cache
                print("Binance API返回格式不符合预期")
        except Exception as e:
            print(f"Binance API错误: {e}")

        # 尝试CoinGecko API
        try:
            print("\n尝试从CoinGecko获取价格...")
            response = requests.get(self.coingecko_api_url, timeout=10)
            print(f"CoinGecko API状态码: {response.status_code}")
            print(f"CoinGecko返回内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'bitcoin' in data and 'usd' in data['bitcoin']:
                    self._btc_price_cache = float(data['bitcoin']['usd'])
                    return self._btc_price_cache
                print("CoinGecko API返回格式不符合预期")
        except Exception as e:
            print(f"CoinGecko API错误: {e}")

        # 尝试OKX API
        try:
            print("\n尝试从OKX获取价格...")
            response = requests.get(self.okx_api_url, timeout=10)
            print(f"OKX API状态码: {response.status_code}")
            print(f"OKX返回内容: {response.text}")
            
            if response.status_code == 200:
                data = response.json()
                if isinstance(data, dict) and 'data' in data and len(data['data']) > 0:
                    self._btc_price_cache = float(data['data'][0]['last'])
                    return self._btc_price_cache
                print("OKX API返回格式不符合预期")
        except Exception as e:
            print(f"OKX API错误: {e}")

        print("所有API都失败了")
        return None

    def get_network_difficulty(self, use_cache=False):
        """
        获取当前网络难度
        :param use_cache: 是否使用缓存的难度
        """
        if use_cache and self._network_difficulty_cache is not None:
            return self._network_difficulty_cache

        try:
            print("\n获取网络难度...")
            response = requests.get(self.difficulty_api_url, timeout=10)
            print(f"难度API状态码: {response.status_code}")
            print(f"难度API返回内容: {response.text}")
            
            if response.status_code == 200:
                self._network_difficulty_cache = float(response.text)
                return self._network_difficulty_cache
        except Exception as e:
            print(f"获取网络难度时出错: {e}")
        return None

    def calculate_mining_revenue(self, hashrate_th, use_cache=False):
        """
        计算挖矿收益
        :param hashrate_th: 算力（TH/s）
        :param use_cache: 是否使用缓存的难度数据
        :return: 每日预期比特币收益
        """
        difficulty = self.get_network_difficulty(use_cache)
        if not difficulty:
            print("无法获取网络难度，无法计算收益")
            return 0
        
        # 将TH/s转换为H/s
        hashrate = hashrate_th * 1e12
        
        # 每天产生的区块数
        blocks_per_day = 144  # 平均每10分钟一个区块
        
        # 全网每秒哈希数
        network_hashrate = difficulty * 2**32 / 600
        
        # 计算每日预期收益
        daily_btc = (hashrate / network_hashrate) * blocks_per_day * self.block_reward
        
        print(f"\n计算详情:")
        print(f"输入算力: {hashrate_th} TH/s")
        print(f"网络难度: {difficulty}")
        print(f"全网算力: {network_hashrate/1e12:.2f} TH/s")
        print(f"区块奖励: {self.block_reward} BTC")
        print(f"预期每日收益: {daily_btc:.8f} BTC")
        
        return daily_btc

    def calculate_power_cost(self, power_watts, electricity_cost_kwh):
        """
        计算每日电力成本
        :param power_watts: 功率（瓦特）
        :param electricity_cost_kwh: 每千瓦时电费（美元）
        :return: 每日电费成本（美元）
        """
        daily_kwh = (power_watts * 24) / 1000
        daily_cost = daily_kwh * electricity_cost_kwh
        
        print(f"\n电力成本计算:")
        print(f"日耗电量: {daily_kwh:.2f} kWh")
        print(f"电费单价: ${electricity_cost_kwh}/kWh")
        print(f"每日电费: ${daily_cost:.2f}")
        
        return daily_cost

    def calculate_roi(self, hashrate_th, power_watts, electricity_cost_kwh, hardware_cost, 
                     pool_fee_percent=2.0, maintenance_cost_yearly=0, hardware_depreciation_yearly=0,
                     block_reward=None, use_cache=False):
        """
        计算投资回报分析
        :param hashrate_th: 算力（TH/s）
        :param power_watts: 功率（瓦特）
        :param electricity_cost_kwh: 每千瓦时电费（美元）
        :param hardware_cost: 硬件成本（美元）
        :param pool_fee_percent: 矿池手续费百分比
        :param maintenance_cost_yearly: 年度维护成本（美元）
        :param hardware_depreciation_yearly: 年度硬件折旧（美元）
        :param block_reward: 区块奖励（BTC）
        :param use_cache: 是否使用缓存的价格和难度数据
        :return: 投资分析报告
        """
        print("\n开始ROI分析...")
        
        if block_reward is not None:
            self.block_reward = block_reward
        
        btc_price = self.get_btc_price(use_cache)
        network_difficulty = self.get_network_difficulty(use_cache)
        
        if not btc_price or not network_difficulty:
            print("无法获取比特币价格或网络难度，无法计算ROI")
            return None

        print(f"当前BTC价格: ${btc_price:,.2f}")
        
        daily_btc = self.calculate_mining_revenue(hashrate_th, use_cache)
        # 扣除矿池手续费
        daily_btc = daily_btc * (1 - pool_fee_percent / 100)
        
        daily_revenue_usd = daily_btc * btc_price
        daily_power_cost = self.calculate_power_cost(power_watts, electricity_cost_kwh)
        
        # 计算每日维护和折旧成本
        daily_maintenance_cost = maintenance_cost_yearly / 365
        daily_depreciation = hardware_depreciation_yearly / 365
        
        # 计算总日常成本
        daily_total_cost = daily_power_cost + daily_maintenance_cost + daily_depreciation
        daily_profit = daily_revenue_usd - daily_total_cost

        # 计算回报周期（天）
        if daily_profit > 0:
            roi_days = hardware_cost / daily_profit
        else:
            roi_days = float('inf')
            print("警告: 当前配置下无法盈利!")

        return {
            'BTC当前价格': btc_price,
            '网络难度': network_difficulty,
            '每日BTC收益(含矿池费)': daily_btc,
            '每日收入(USD)': daily_revenue_usd,
            '每日电费(USD)': daily_power_cost,
            '每日维护成本(USD)': daily_maintenance_cost,
            '每日折旧(USD)': daily_depreciation,
            '每日总成本(USD)': daily_total_cost,
            '每日净利润(USD)': daily_profit,
            '预计回本天数': roi_days,
            '月度净利润(USD)': daily_profit * 30,
            '年度净利润(USD)': daily_profit * 365,
            '矿池手续费': pool_fee_percent,
            '年度维护成本(USD)': maintenance_cost_yearly,
            '年度折旧(USD)': hardware_depreciation_yearly
        }

def main():
    # 示例参数
    HASHRATE_TH = 200  # 200 TH/s
    POWER_WATTS = 3500  # 3500W
    ELECTRICITY_COST = 0.01  # $0.01 per kWh
    HARDWARE_COST = 4000  # $4000

    print("=== 比特币挖矿收益分析器 ===")
    print(f"版本: 1.1")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\n初始参数:")
    print(f"算力: {HASHRATE_TH} TH/s")
    print(f"功耗: {POWER_WATTS}W")
    print(f"电费: ${ELECTRICITY_COST}/kWh")
    print(f"硬件成本: ${HARDWARE_COST}")

    calculator = BTCMiningCalculator()
    result = calculator.calculate_roi(
        hashrate_th=HASHRATE_TH,
        power_watts=POWER_WATTS,
        electricity_cost_kwh=ELECTRICITY_COST,
        hardware_cost=HARDWARE_COST
    )

    if result:
        print("\n=== 最终分析结果 ===")
        for key, value in result.items():
            if isinstance(value, float):
                if 'BTC' in key:
                    print(f"{key}: {value:.8f}")
                elif 'USD' in key or '价格' in key:
                    print(f"{key}: ${value:,.2f}")
                else:
                    print(f"{key}: {value:.2f}")
            else:
                print(f"{key}: {value}")

if __name__ == "__main__":
    main() 