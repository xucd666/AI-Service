from tools.dish_tool import get_low_fat_dishes


LOWEST_CALORIE_KEYWORDS = (
    "最低",
    "最少",
    "最小",
    "热量低",
    "热量最低",
    "卡路里最低",
    "卡路里最少",
)


def query_dishes_node(state):
    result = get_low_fat_dishes()

    if not result.get("success"):
        state["final_answer"] = "减脂餐查询失败，请稍后再试。"
        state["dishes"] = []
        return state

    state["dishes"] = result.get("data", [])
    return state


def route_dish_query(state):
    user_input = state.get("user_input", "")

    if any(keyword in user_input for keyword in LOWEST_CALORIE_KEYWORDS):
        return "select_lowest_calorie"

    return "answer_dish_list"


def select_lowest_calorie_node(state):
    dishes = state.get("dishes") or []

    if not dishes:
        state["best_dish"] = None
        return state

    best_dish = min(
        dishes,
        key = lambda dish : dish.get("calories",99999)
    )

    state["best_dish"] = best_dish
    return state


def answer_dish_list_node(state):
    dishes = state.get("dishes") or []

    if state.get("final_answer"):
        return state

    if not dishes:
        state["final_answer"] = "当前没有查询到减脂餐。"
        return state

    lines = []
    for dish in dishes:
        name = dish.get("name", "未知菜品")
        calories = dish.get("calories", "热量未知")
        lines.append(f"- {name}，约 {calories} 大卡")

    state["final_answer"] = "查询到以下减脂餐：\n" + "\n".join(lines)
    return state


def answer_dish_node(state):
    best_dish = state.get("best_dish")

    if state.get("final_answer"):
        return state

    if not best_dish:
        state["final_answer"] = "当前没有查询到合适的减脂餐。"
        return state

    name = best_dish.get("name", "未知菜品")
    calories = best_dish.get("calories", "热量未知")

    state["final_answer"] = f"当前热量最低的减脂餐是：{name}，约 {calories} 大卡。"
    return state
