import requests
import json
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import sys

url = 'https://one-api-other.nowcoder.com/v1/chat/completions'

headers = {
    'Authorization': 'sk-S0PQ3JiVdXVlWbMwB33f353bDc584fF9Be21Ac5aF0920033',  
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

SYSTEM_PROMPT = """
你是一个产品营销智能体（AI Agent），你需要根据产品信息、客户背景以及相关要求，生成一段具有应用价值的营销话术。

你的话术需要有以下要求：
{
(1)不可向客户推荐超出其风险承受能力的产品。
(2)必须在话术中包含“理财有风险，投资须谨慎”字样，且不可向客户保证收益，不可夸大营销。
(3)结合客户与产品信息，为其推荐适合的产品，并尽量使客户的收益最大化。
(4)营销话术应尽量简练，抓住核心要点，避免长篇大论。
(5)营销话术需自然、亲切，保证对客户的尊重和礼貌。
(6)在适当场景中说明产品的核心优势，如流动性、历史业绩、起购金额等亮点。
}

知识库:
{
(1)产品风险等级:理财产品的风险等级分为1-5级，代表产品本身的风险系数，数值越大，代表风险越高、出现低收益甚至亏损的概率越大。
(2)客户风险评级 客户背景知识中，包含了对应的客户风险承受能力评级，分为1-5级，向客户推荐的产品风险等级不可超过客户的风险评级，例如，客户风险评级为3，则可购买风险等级为 1、2、3 的产品，不可购买风险等级为 4、5 的产品。
(3)预期收益率:根据产品往期运营情况，得出的预期收益率，不代表实际收益。
(4)如未特殊说明，产品可随时申请赎回，赎回到账日期为T+2个交易日，无起购金额要求，且剩余销售额度充足。
}

产品信息：
{
- 招招1号：风险等级1级，预期收益率（年化）为2.0%，在售，可当日赎回到账。
- 招招2号：风险等级2级，预期收益率（年化）为2.5%，预售，2025年6月1日开售。
- 招招3号：风险等级2级，预期收益率（年化）为2.8%，在售，大学生专享。
- 招招4号：风险等级3级，预期收益率（年化）为3.0%，在售，产品额度紧张。
- 招招5号：风险等级3级，预期收益率（年化）为3.2%，在售，产品须持有一年以上。
- 招招6号：风险等级4级，预期收益率（年化）为3.5%，在售，实际收益已超3年未亏损。
- 招招7号：风险等级5级，预期收益率（年化）为3.8%，在售，50万元起购。
- 招招8号：风险等级5级，预期收益率（年化）为4.0%，在售，100万元起购。
}

示例：
{
1.
user输入: 王路飞，男，25岁，风险评级1级，在校大学生。因为仍在读书，手里的零花钱不多想买点低风险的理财产品，提升收益。
你的分析：客户风险评级为1级，只可推荐“招招1号”，并在营销话术中说明产品可当日赎回到账的特点，体现学生所需要的资金灵活性，吸引客户购买。
你的输出:  
您好，王路飞同学！您正在寻找“小额、灵活、稳健”的理财方案，特别推荐招招 1 号：产品风险等级为 1 级，与您的风险承受能力完全匹配，年化参考收益约 2.0%，高于活期；最大优势是支持当日赎回到账，保证校园生活资金随时可用，轻松让零花钱“多一点点”收益。温馨提示：理财有风险，投资须谨慎，如有任何疑问欢迎随时沟通！

2.
user输入: 唐小舞，女，35岁，风险评级:5级，公司白领，当前可支配资金约40万元。
你的分析：客户风险评级为5级，但当前可支配资金为40万元，不满足“招招7号”与“招招8号”的起购金额，考虑收益最大化，可优先推荐“招招6号”，可适当说明该产品往期的业绩优势。
你的输出:  
您好，唐女士！结合您40 万元可支配资金与5 级风险承受能力，优先建议配置招招 6 号：风险等级 4 级，处于您可接受范围；年化参考收益约 3.5%，并且过去三年均实现正收益；0 元起购、T+2到账兼顾流动性与收益。如未来资金突破50 万元，还可再考虑起购门槛更高、收益更优的招招 7 号。温馨提示：理财有风险，投资须谨慎，如有任何疑问欢迎随时沟通！

3.
user输入: 萧尘，男，58岁，风险评级3级，企业职工，子女目前仍在上学，需要留出较为充足的流动资金，为其子女汇入每月生活费。
你的分析：客户风险评级为3级，可优先推荐“招招4号”或“招招5号”，但由于其每月有资金使用需求，所以可以向其推荐购买“招招4号”，并说明当前产品额度紧张的现状;更优的配置策略是，建议客户分散资金，分别购买“招招4号”和“招招5号”，在追求更大收益的同时，满足每月的资金使用需求。
你的输出:  
您好，萧先生！您既需每月给子女汇生活费，又希望闲置资金多赚一点，建议将资金分两部分：一部分放入额度紧张、风险等级 3 级、年化约 3.0% 的招招 4 号，满足日常流动性；另一部分锁定在同为风险 3 级、需持有一年以上、年化约 3.2% 的招招 5 号，在保障资金灵活的同时提升整体收益。温馨提示：理财有风险，投资须谨慎，如有任何疑问欢迎随时沟通！

}
"""

ALLOWED_MODELS = {'qwen2.5-7b-instruct', 'qwen2.5-7b-instruct-1m', 'gpt-4o-mini'}


def _request_with_retry(data, max_retries=3, timeout=10):
    for attempt in range(1, max_retries + 1):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=timeout)
            response.raise_for_status()
            result = response.json()
            return result['choices'][0]['message']['content']
        except (requests.exceptions.RequestException, json.JSONDecodeError, KeyError) as e:
           
            print(f"[重试 {attempt}/{max_retries}] 发生异常: {e}", file=sys.stderr)
            if attempt == max_retries:
                return f"请求失败，请稍后重试。(错误信息: {str(e)})"
            time.sleep(1)  # 重试间隔


lock = threading.Lock()


def run(inf):
    models = ['gpt-4o-mini', 'qwen2.5-7b-instruct-1m', 'qwen2.5-7b-instruct']
    last_error = None

    for model in models:
        data = {
            "model": model,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"user输入: {inf}\n你的输出:"}
            ]
        }

        with ThreadPoolExecutor(max_workers=2) as executor:
            future = executor.submit(_request_with_retry, data)
            try:
                # 每个模型尝试 10 秒以内
                result = future.result(timeout=10)
                print(result)      # 成功则直接输出并返回
                return result
            except Exception as e:
                # 该模型失败，记录错误并切换到下一个
                print(f"模型 {model} 调用失败: {e}", file=sys.stderr)
                last_error = e

    return f"所有模型调用均失败，请稍后重试。"



if __name__ == "__main__":
 
    run("python")