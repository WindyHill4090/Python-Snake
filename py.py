import random  # 用于随机生成食物的位置。
import time  # 用于计算游戏已经运行的时间。
import tkinter as tk  # 导入 Python 自带的图形界面库。
from collections import deque  # 导入队列，用于自动寻路的广度优先搜索。

SIZE = 20  # 设置每个格子的宽度和高度。
WIDTH = 500  # 设置游戏区域的宽度。
HEIGHT = 400  # 设置游戏区域的高度。
TICK = 220  # 设置蛇每次移动之间的间隔，单位为毫秒。
SEARCH_LIMIT = 20000  # 限制每次自动寻路最多检查的状态数量。

root = tk.Tk()  # 创建游戏主窗口。
root.title("贪吃蛇")  # 设置窗口标题。

score = 0  # 保存当前游戏得分。
snake = []  # 保存蛇身体各节的位置，第一项是蛇头。
direction = (SIZE, 0)  # 保存蛇当前移动的方向，初始向右。
food = (0, 0)  # 保存食物当前所在的格子坐标。
paused = False  # 记录游戏是否处于暂停状态。
game_over = False  # 记录游戏是否已经结束。
start_time = 0  # 保存本局游戏的开始时间。
planned_path = []  # 保存自动寻路得到的后续移动步骤。

label = tk.Label(root, text="分数：0   时间：00:00   自动模式")  # 创建显示分数和时间的文字标签。
label.pack()  # 将状态标签放入窗口并显示。

canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg="black")  # 创建黑色游戏画布。
canvas.pack()  # 将游戏画布放入窗口并显示。


def format_time(seconds):  # 定义把秒数转换成分:秒格式的函数。
    minutes = seconds // 60  # 计算完整的分钟数。
    secs = seconds % 60  # 计算扣除整分钟后剩余的秒数。
    return "{:02d}:{:02d}".format(minutes, secs)  # 返回两位数的分钟和秒数。


def update_status():  # 定义刷新分数和计时器显示的函数。
    elapsed = int(time.time() - start_time) if not game_over else int(time.time() - start_time)  # 计算从本局开始到现在经过的秒数。
    label.config(text="分数：{}   时间：{}".format(score, format_time(elapsed)))  # 更新窗口中的分数和用时。


def place_food():  # 定义随机放置食物的函数。
    while True:  # 持续尝试，直到找到不在蛇身上的位置。
        x = random.randrange(0, WIDTH, SIZE)  # 随机选择食物的横坐标格子。
        y = random.randrange(0, HEIGHT, SIZE)  # 随机选择食物的纵坐标格子。
        if (x, y) not in snake:  # 检查这个位置是否没有被蛇占据。
            return (x, y)  # 返回可用的食物位置。


def restart_game():  # 定义重新开始一局游戏的函数。
    global score, snake, direction, food, paused, game_over, start_time, planned_path  # 声明本函数会修改这些全局变量。
    score = 0  # 将得分清零。
    snake = [(100, 100), (80, 100), (60, 100)]  # 在画布左上区域放置初始的三节蛇身。
    direction = (SIZE, 0)  # 将蛇的初始移动方向设为向右。
    food = place_food()  # 随机放置新一局的食物。
    paused = False  # 确保新一局不是暂停状态。
    game_over = False  # 清除上一局的游戏结束状态。
    planned_path = []  # 清除上一局残留的自动寻路路线。
    start_time = time.time()  # 记录新一局的开始时间。
    update_status()  # 更新分数和计时器显示。
    draw()  # 绘制新一局的蛇和食物。
    move()  # 启动新一局的自动移动循环。


def pause_game():  # 定义切换暂停和继续状态的函数。
    global paused  # 声明本函数会修改全局暂停状态。
    if not game_over:  # 只有游戏尚未结束时才允许切换暂停。
        paused = not paused  # 将暂停状态切换为相反状态。
        draw()  # 重新绘制画面以显示或移除暂停提示。


def change_direction(event):  # 定义处理键盘事件的函数。
    if event.keysym.lower() == "p" and not game_over:  # 检查用户是否按下 P 且游戏尚未结束。
        pause_game()  # 按 P 键时切换暂停或继续状态。


def auto_direction():  # 定义搜索一条不撞蛇身并能到达食物的路线。
    initial = tuple(snake)  # 将当前蛇身转换成不可变状态，作为搜索起点。
    queue = deque([initial])  # 创建队列并放入起始蛇身状态。
    parents = {initial: None}  # 记录每种蛇身状态的前一个状态，用于最后还原路线。
    steps = [(SIZE, 0), (0, SIZE), (-SIZE, 0), (0, -SIZE)]  # 列出向右、向下、向左和向上的移动方向。
    checked = 0  # 初始化已经检查过的状态数量。

    while queue and checked < SEARCH_LIMIT:  # 队列未空且搜索次数未超过上限时继续搜索。
        body = queue.popleft()  # 取出队列中最早加入的蛇身状态。
        checked += 1  # 将已检查状态数量加一。
        head = body[0]  # 取出当前状态中的蛇头位置。
        ordered_steps = sorted(  # 根据离食物的距离排序可能的移动方向。
            steps,  # 对四种相邻移动方向排序。
            key=lambda step: abs(head[0] + step[0] - food[0])  # 计算移动后横坐标与食物横坐标的距离。
            + abs(head[1] + step[1] - food[1]),  # 加上移动后纵坐标与食物纵坐标的距离。
        )  # 完成方向排序，让搜索优先尝试接近食物的方向。

        for step in ordered_steps:  # 依次尝试排序后的移动方向。
            cell = (head[0] + step[0], head[1] + step[1])  # 计算移动后蛇头所在的格子。
            eating = cell == food  # 判断这一步是否会吃到食物。
            occupied = body if eating else body[:-1]  # 吃食物时蛇尾不移动，否则蛇尾会腾出位置。
            if (  # 开始检查新蛇头是否会导致碰撞。
                cell[0] < 0 or cell[0] >= WIDTH  # 检查新蛇头是否超出左右边界。
                or cell[1] < 0 or cell[1] >= HEIGHT  # 检查新蛇头是否超出上下边界。
                or cell in occupied  # 检查新蛇头是否撞到不会移动离开的蛇身。
            ):  # 结束碰撞条件的检查。
                continue  # 跳过会导致碰撞的方向。

            next_body = (cell,) + (body if eating else body[:-1])  # 根据是否吃到食物计算移动后的完整蛇身。
            if next_body in parents:  # 检查这个蛇身状态是否已经搜索过。
                continue  # 已经搜索过就跳过，避免重复搜索。
            parents[next_body] = (body, step)  # 记录该状态的来源状态和走到这里所用的方向。

            if eating:  # 如果新蛇头到达食物位置，说明已经找到路线。
                path = []  # 创建列表，用来保存还原出来的路线。
                current = next_body  # 从吃到食物后的蛇身状态开始回溯。
                while parents[current] is not None:  # 一直回溯到搜索起始状态。
                    previous, move = parents[current]  # 取出上一个状态和到达当前状态的移动方向。
                    path.append(move)  # 将这一步移动方向加入路线。
                    current = previous  # 继续回到前一个蛇身状态。
                path.reverse()  # 将倒序收集的路线反转为实际移动顺序。
                return path  # 返回找到的完整安全路线。

            queue.append(next_body)  # 将可安全到达的新蛇身状态放入队列继续搜索。

    return []  # 搜索结束仍未找到路线时返回空列表。


def safe_direction():  # 定义找不到食物路线时选择安全移动方向的函数。
    head = snake[0]  # 取出当前蛇头位置。
    steps = [(SIZE, 0), (0, SIZE), (-SIZE, 0), (0, -SIZE)]  # 列出四种可选移动方向。
    safe_steps = []  # 创建列表保存不会立即撞墙或撞身的方向。
    for step in steps:  # 逐个检查每个移动方向。
        cell = (head[0] + step[0], head[1] + step[1])  # 计算该方向移动后的蛇头位置。
        occupied = snake if cell == food else snake[:-1]  # 如果吃食物蛇尾不动，否则忽略即将移动的蛇尾。
        if (  # 开始检查这一步是否安全。
            0 <= cell[0] < WIDTH  # 检查横坐标仍在画布范围内。
            and 0 <= cell[1] < HEIGHT  # 检查纵坐标仍在画布范围内。
            and cell not in occupied  # 检查新位置没有被蛇身占据。
        ):  # 结束安全条件检查。
            safe_steps.append(step)  # 将安全方向加入候选列表。
    if safe_steps:  # 如果至少找到一个安全方向。
        return min(  # 返回候选方向中最接近食物的方向。
            safe_steps,  # 从已检查过的安全方向中选择。
            key=lambda step: abs(head[0] + step[0] - food[0])  # 计算移动后横向离食物的距离。
            + abs(head[1] + step[1] - food[1]),  # 加上移动后纵向离食物的距离。
        )  # 完成距离比较并返回最优的安全方向。
    return direction  # 没有安全方向时保持当前方向，后续碰撞判断会结束游戏。


def draw():  # 定义重绘游戏画面的函数。
    canvas.delete("all")  # 清除画布上上一帧的所有图形。
    canvas.create_rectangle(food[0], food[1], food[0] + SIZE, food[1] + SIZE, fill="red")  # 用红色方块绘制食物。
    for x, y in snake:  # 遍历蛇身上每一节的位置。
        canvas.create_rectangle(x, y, x + SIZE, y + SIZE, fill="lime")  # 用绿色方块绘制当前蛇身这一节。
    if paused and not game_over:  # 如果游戏处于暂停状态且尚未结束。
        canvas.create_text(WIDTH / 2, HEIGHT / 2, text="已暂停", fill="white", font=("", 22))  # 在画布中央显示暂停文字。
    if game_over:  # 如果游戏已经结束。
        canvas.create_text(WIDTH / 2, HEIGHT / 2, text="游戏结束", fill="white", font=("", 24))  # 在画布中央显示游戏结束文字。


def move():  # 定义蛇每次自动移动一步的函数。
    global score, snake, food, paused, game_over, direction, planned_path  # 声明本函数会修改的全局游戏状态。
    if not game_over and not paused:  # 仅在游戏进行且未暂停时移动蛇。
        if not planned_path:  # 如果当前没有剩余计划路线。
            planned_path = auto_direction()  # 搜索一条通往食物的安全路线。
        direction = planned_path.pop(0) if planned_path else safe_direction()  # 使用路线下一步，或退而选择安全方向。
        x = snake[0][0] + direction[0]  # 根据方向计算新蛇头的横坐标。
        y = snake[0][1] + direction[1]  # 根据方向计算新蛇头的纵坐标。
        head = (x, y)  # 将新蛇头坐标组合成一个位置元组。
        eating = head == food  # 判断新蛇头是否会吃到食物。

        if (  # 开始判断蛇是否发生碰撞。
            x < 0 or x >= WIDTH or y < 0 or y >= HEIGHT  # 检查蛇头是否撞到游戏区域边界。
            or head in (snake if eating else snake[:-1])  # 检查蛇头是否撞上身体，普通移动时允许进入腾空的尾格。
        ):  # 结束碰撞条件判断。
            game_over = True  # 将游戏状态设为结束。
            draw()  # 重绘画面并显示结束提示。
            update_status()  # 刷新最终分数和时间。
            return  # 停止本次移动，不再安排下一次移动。

        snake.insert(0, head)  # 将新蛇头放到蛇身列表的最前面。
        if head == food:  # 如果蛇头到达食物位置。
            score += 1  # 将分数增加一分。
            food = place_food()  # 在蛇身以外随机放置下一份食物。
            planned_path = []  # 清除旧食物对应的路线，以便重新规划。
        else:  # 如果这一步没有吃到食物。
            snake.pop()  # 删除蛇尾一节，使蛇的长度保持不变。

        update_status()  # 刷新分数和计时器。
        draw()  # 绘制移动后的蛇和食物。

    root.after(TICK, move)  # 等待设定的时间后再次调用本函数，形成游戏循环。


root.bind("<Key>", change_direction)  # 将键盘按键事件绑定到处理函数（P 键可暂停/继续）。
restart_game()  # 初始化并启动一局新游戏。
root.mainloop()  # 启动 Tkinter 事件循环并保持窗口运行。
