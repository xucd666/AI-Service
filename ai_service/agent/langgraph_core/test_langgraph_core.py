from agent.langgraph_core.service import chat_with_langgraph

if __name__ == "__main__":
    tests = [
        "帮我查询订单1774855083625",
        "我想吃减脂餐",
        "帮我推荐热量最低的减脂餐",
        "今天天气怎么样"
    ]

    for text in tests:
        print("=" * 50)
        print("用户：", text)

        result = chat_with_langgraph(text)

        print("AI：", result["answer"])
        print("State：", result["state"])