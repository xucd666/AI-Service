from tools.dish_tool import get_low_fat_dishes


def query_dishes_node(state):
    dishes = get_low_fat_dishes()
    state["dishes"] = dishes
    return state

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

def answer_dish_node(state):
    best_dish = state.get("best_dish")

    if not best_dish:
        state["final_answer"] = "当前没有查询到合适的减脂餐。"
        return state

    name = best_dish.get("name", "未知菜品")
    calories = best_dish.get("calories", "热量未知")

    state["final_answer"] = f"当前热量最低的减脂餐是：{name}，约 {calories} 大卡。"
    return state