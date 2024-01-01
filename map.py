"""
21电子信息工程数据结构课设内容
小组成员：颜天煜 王海博 田延翔 张家璇
选题：第六题
题目描述：
某个城市的地图由多个交叉路口和道路组成。每个交叉路口可以表示为一个节点，并且每条道路可以表示为两个节点之间的边。请设计一个图的数据结构编写相应的
算法来完成以下功能，并实现可交互GUI界面(非控制台窗口)显示完整的地图和所有功能。

基本要求：
（1）实现添加交叉路口和道路的功能，能够根据输入的交叉路口和道路信息搭建整个城市地图。
（2）实现删除交叉路口和道路的功能，能够根据输入的交叉路口或道路信息删除对应的元素。
（3）实现查找给定交叉路口之间的最短路径的功能，使用Dijkstra算法或其他最短路径算法。
（4）实现查找给定交叉路口的所有相邻交叉路口的功能。
（5）实现检测是否存在闭合环路的功能，即判断图中是否存在从某个交叉路口出发能回到自身的路径。
补充说明：
（1）交叉路口信息包括唯一的路口ID和位置坐标。
（2）道路信息包括起始交叉路口ID、目标交叉路口ID和道路长度。

不足之处：
1.缩放的改进，无法实现高亮对齐
2.添加删除可以采取列表形式的显示
3.如何添加mysql的存取
4.代码的重构，迪杰斯特拉部分以及显示部分，响应按钮try except，显示的继承类
"""
import tkinter as tk
from tkinter import messagebox
import heapq
import random
import pandas as pd
import webbrowser

"""参数部分，便于修改"""
# 显示结点的半径
draw_radius = 10
# 缩放与位置参数
var_x = 40
var_add = 50


class CityMap:
    def __init__(self):
        # 存储地图信息的字典，每个交叉路口有唯一的标识符，包含坐标和相邻道路信息，还有一个流量信息
        self.graph = {}

    def add_intersection(self, intersection_id, coordinates, flow):
        """添加交叉路口到地图中."""
        if intersection_id not in self.graph:
            self.graph[intersection_id] = {'coordinates': coordinates, 'roads': {}, 'flow': flow}
        else:
            messagebox.showerror("错误", "该结点id与已存在的结点重复，请更换！")
            print("该结点id与已存在的结点重复，请更换！")

    def add_road(self, start_intersection, end_intersection, length):
        """添加道路到地图中."""
        if start_intersection in self.graph and end_intersection in self.graph:
            # 分别给两个结点添加互相道路信息
            self.graph[start_intersection]['roads'][end_intersection] = length
            self.graph[end_intersection]['roads'][start_intersection] = length
        else:
            messagebox.showerror("错误", "结点错误，道路添加错误！")
            print("道路添加错误！")

    def init_1(self):
        """示例1 实验的那个内容"""
        # 添加交叉路口
        self.add_intersection("A", (0, 0), 0)
        self.add_intersection("B", (2, 0), 0)
        self.add_intersection("C", (3, 1), 0)
        self.add_intersection("D", (2, 2), 0)
        self.add_intersection("E", (0, 2), 0)
        self.add_intersection("F", (1, 1), 0)
        # 添加道路
        self.add_road("A", "B", 31)
        self.add_road("A", "E", 21)
        self.add_road("A", "F", 11)
        self.add_road("B", "F", 8)
        self.add_road("B", "D", 18)
        self.add_road("B", "C", 7)
        self.add_road("E", "F", 9)
        self.add_road("E", "D", 29)
        self.add_road("D", "F", 23)
        self.add_road("D", "C", 12)

    def init_2(self):
        """获取excel数据，得到学校部分节点距离图"""
        try:
            excel_file_path = 'cumt_data2.xlsx'
            df = pd.read_excel(excel_file_path)
            for index, row in df.iterrows():
                intersection_id = row['ID']
                coordinates = (row['x'], row['y'])
                # 添加交叉路口到地图
                self.add_intersection(intersection_id, coordinates, 0)
            for index, row in df.iterrows():
                # 添加相邻道路到地图 两个循环不能写到一起 必须先确定所有的结点，否则道路添加失败，还没初始化
                intersection_id = row['ID']
                for i in range(3, len(row.index), 2):
                    adjacent_intersection = row.iloc[i]
                    if pd.notna(adjacent_intersection):
                        road_length = row.iloc[i + 1]
                        self.add_road(intersection_id, adjacent_intersection, road_length)
        except:
            messagebox.showerror("错误", "初始化失败，请检查数据文件是否存在，数据文件格式是否正确！")

    def remove_intersection(self, intersection_id):
        """删除交叉路口及与之相关的道路."""
        if intersection_id in self.graph:
            # 删除交叉路口
            del self.graph[intersection_id]
            # 删除与该路口相关的道路
            for intersection in self.graph:
                if intersection_id in self.graph[intersection]['roads']:
                    del self.graph[intersection]['roads'][intersection_id]
        else:
            messagebox.showerror("错误", "所删除的节点不存在！")
            print("所删除的结点不存在")

    def remove_road(self, start_intersection, end_intersection):
        """删除一条道路."""
        if start_intersection in self.graph and end_intersection in self.graph:
            # 删除两个交叉路口之间的双向道路，两侧都要删除
            if end_intersection in self.graph[start_intersection]['roads']:
                del self.graph[start_intersection]['roads'][end_intersection]
            if start_intersection in self.graph[end_intersection]['roads']:
                del self.graph[end_intersection]['roads'][start_intersection]
        else:
            messagebox.showerror("错误", "所删除的道路不存在！")
            print("所删除的道路不存在")

    def shortest_path(self, start_intersection, end_intersection):
        """查找给定交叉路口之间的最短路径长度，使用 Dijkstra 算法."""
        if start_intersection in self.graph and end_intersection in self.graph:
            distances = {intersection: float('inf') for intersection in self.graph}
            distances[start_intersection] = 0
            visited = set()
            priority_queue = [(0, start_intersection)]

            while priority_queue:
                current_distance, current_intersection = heapq.heappop(priority_queue)

                if current_intersection in visited:
                    continue

                visited.add(current_intersection)

                for neighbor, road_length in self.graph[current_intersection]['roads'].items():
                    distance = current_distance + road_length
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        heapq.heappush(priority_queue, (distance, neighbor))

            return distances[end_intersection]
        else:
            messagebox.showerror("错误", "结点不存在！")

    def adjacent_intersections(self, intersection_id):
        """查找给定交叉路口的所有相邻交叉路口."""
        if intersection_id in self.graph:
            return list(self.graph[intersection_id]['roads'].keys())
        else:
            messagebox.showerror("错位", "所查找结点不存在！")

    def has_cycle(self):
        """检测是否存在闭合环路."""
        visited = set()

        def dfs(current_intersection, parent):
            visited.add(current_intersection)
            for neighbor in self.graph[current_intersection]['roads']:
                if neighbor not in visited:
                    if dfs(neighbor, current_intersection):
                        return True
                elif neighbor != parent:
                    return True
            return False

        for intersection in self.graph:
            if intersection not in visited:
                if dfs(intersection, None):
                    return True
        return False

    def shortest_path_nodes(self, start_intersection, end_intersection):
        """查找给定交叉路口之间的最短路径，使用 Dijkstra 算法."""
        if start_intersection in self.graph and end_intersection in self.graph:
            distances = {intersection: float('inf') for intersection in self.graph}
            distances[start_intersection] = 0
            predecessors = {intersection: None for intersection in self.graph}
            priority_queue = [(0, start_intersection)]

            while priority_queue:
                current_distance, current_intersection = heapq.heappop(priority_queue)

                for neighbor, road_length in self.graph[current_intersection]['roads'].items():
                    distance = current_distance + road_length
                    if distance < distances[neighbor]:
                        distances[neighbor] = distance
                        predecessors[neighbor] = current_intersection
                        heapq.heappush(priority_queue, (distance, neighbor))

            # 从结束结点回溯找到最短路径上的所有节点
            path_nodes = []
            current_intersection = end_intersection
            while current_intersection is not None:
                path_nodes.insert(0, current_intersection)
                current_intersection = predecessors[current_intersection]

            return path_nodes
        else:
            messagebox.showerror("错误", "结点不存在！")

    def print_all_nodes(self):
        """打印所有节点信息."""
        print("所有交叉口信息")
        for intersection_id, data in self.graph.items():
            print(f"城市: {intersection_id}, 位置: {data['coordinates']}, 连接道路: {data['roads']}, 流量：{data['flow']}")
        print("\n")

    def car_Flow(self, flow):
        """需要修改，不能直接用"""
        for i in range(flow):
            start = random.choice(list(self.graph.keys()))
            end = random.choice(list(self.graph.keys()))
            # 找到从start到end的最短路径
            shortest_path_nodes = self.shortest_path_nodes(start, end)
            # 将最短路径上所有结点的flow+1
            for node in shortest_path_nodes:
                self.graph[node]['flow'] += 1

    def draw_map(self, canvas, scale=1.0, x_offset=0, y_offset=0):
        """绘制地图到指定的Canvas上."""
        # 删除Canvas上的所有元素
        canvas.delete("all")
        # 定义拖拽标签的数据
        drag_data = {'x': 0, 'y': 0, 'item': 0}

        def start_drag(event):
            """开始拖动标签."""
            closest_item = canvas.find_closest(event.x, event.y)
            if closest_item:
                drag_data['item'] = closest_item[0]
                drag_data['x'] = event.x
                drag_data['y'] = event.y

        def drag(event):
            """拖动标签."""
            if drag_data['item']:
                canvas.move(drag_data['item'], event.x - drag_data['x'], event.y - drag_data['y'])
                drag_data['x'] = event.x
                drag_data['y'] = event.y

        def stop_drag(event):
            """停止拖动标签."""
            drag_data['item'] = 0

        # 绑定鼠标事件
        canvas.bind("<ButtonPress-1>", start_drag)
        canvas.bind("<B1-Motion>", drag)
        canvas.bind("<ButtonRelease-1>", stop_drag)

        # 缩放和移动地图
        canvas.scale("all", 0, 0, scale, scale)
        canvas.xview_moveto(x_offset)
        canvas.yview_moveto(y_offset)

        # 重新绘制地图
        for intersection_id, data in self.graph.items():
            x, y = data['coordinates']
            x, y = x * var_x + var_add, y * var_x + var_add
            r = draw_radius

            # 在结点旁边显示点的ID
            canvas.create_text(x + r + 5, y, text=str(intersection_id), fill="black", anchor="w", tags="node_text")
            canvas.create_oval(x - r, y - r, x + r, y + r, fill="blue", tags="node_text")

            for neighbor_id, road_length in data['roads'].items():
                neighbor_coordinates = self.graph[neighbor_id]['coordinates']
                neighbor_x, neighbor_y = neighbor_coordinates[0] * var_x + var_add, neighbor_coordinates[1] * var_x \
                                         + var_add  # 后面还有要改

                # 计算线的方向和长度
                dx, dy = neighbor_x - x, neighbor_y - y
                line_length = ((dx) ** 2 + (dy) ** 2) ** 0.5

                # 调整线的起点和终点，使其连接到圆的外边缘,防止在外面比较丑陋
                ratio_start = r / line_length
                ratio_end = (line_length - r) / line_length
                adjusted_start_x = x + dx * ratio_start
                adjusted_start_y = y + dy * ratio_start
                adjusted_end_x = x + dx * ratio_end
                adjusted_end_y = y + dy * ratio_end

                # 在边上显示权值
                canvas.create_text((adjusted_start_x + adjusted_end_x) / 2, (adjusted_start_y + adjusted_end_y) / 2,
                                   text=str(road_length), fill="black", tags="road_text")
                canvas.create_line(adjusted_start_x, adjusted_start_y, adjusted_end_x, adjusted_end_y, tags="road")

    def display_map_gui(self):
        """显示地图的GUI界面."""
        root = tk.Tk()
        root.title("数据结构课设-地图")
        root.geometry("800x800")

        # # 添加下拉列表框，用于选择结点或道路 列表显示 还没添加
        # combo = ttk.Combobox(root)
        # combo.pack(side=tk.LEFT, padx=10, pady=5, anchor="n", fill="y")
        #
        # # 更新下拉列表框内容的方法
        # def update_combobox():
        #     combo['values'] = tuple(self.graph.keys())

        def button_click():
            """仅测试"""
            root_test = tk.Tk()
            root_test.title("test")

            label_test = tk.Label(root_test, text="测试")
            label_test.pack(side=tk.TOP, pady=10)

            root_test.geometry("500x500")
            root_test.mainloop()

        def button_click_add():
            root_add = tk.Tk()
            root_add.title("添加结点")
            root_add.geometry("300x300")
            label_add = tk.Label(root_add, text="请输入想要添加的结点：")
            label_add.pack(side=tk.TOP, padx=10, pady=5, anchor="n", fill="x")

            # 创建三个Frame，每个Frame包含一个标签和一个文本框
            frame_input_name = tk.Frame(root_add)
            frame_input_name.pack(padx=10, pady=5, anchor="n")
            frame_input_x = tk.Frame(root_add)
            frame_input_x.pack(padx=10, pady=5, anchor="n")
            frame_input_y = tk.Frame(root_add)
            frame_input_y.pack(padx=10, pady=5, anchor="n")

            lab_name = tk.Label(frame_input_name, text="名称:")
            entry_name = tk.Entry(frame_input_name)
            lab_x = tk.Label(frame_input_x, text="x:")
            entry_x = tk.Entry(frame_input_x)
            lab_y = tk.Label(frame_input_y, text="y:")
            entry_y = tk.Entry(frame_input_y)

            # 使用pack方法设置布局
            lab_name.pack(side="left", padx=10, pady=5, anchor="w")
            entry_name.pack(side="left", padx=10, pady=5, anchor="w")
            lab_x.pack(side="left", padx=10, pady=5, anchor="w")
            entry_x.pack(side="left", padx=10, pady=5, anchor="w")
            lab_y.pack(side="left", padx=10, pady=5, anchor="w")
            entry_y.pack(side="left", padx=10, pady=5, anchor="w")

            def button_click_ok():
                # 获取用户输入的值
                name_value = entry_name.get()
                x_value = entry_x.get()
                y_value = entry_y.get()

                self.add_intersection(name_value, (int(x_value), int(y_value)), 0)
                self.print_all_nodes()

                self.draw_map(canvas)
                # root_add.destroy()
                # 最后一句可以不做 这样就可以连续添加

            # 创建两个按钮，一个确定，一个取消
            button_ok = tk.Button(root_add, text="确定", command=button_click_ok)
            button_cancel = tk.Button(root_add, text="取消", command=root_add.destroy)

            # 使用pack方法设置布局
            button_ok.pack(side=tk.LEFT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)
            button_cancel.pack(side=tk.RIGHT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)
            # 通过将 fill 设置为 tk.X，按钮会充满水平方向的可用空间。expand=True 则表示在有多余空间时扩展按钮以填充整个可用空间。

        def button_click_add_road():
            root_add_road = tk.Tk()
            root_add_road.title("添加道路")
            root_add_road.geometry("300x300")
            label_add = tk.Label(root_add_road, text="请输入想要添加的道路：")
            label_add.pack(side=tk.TOP, padx=10, pady=5, anchor="n", fill="x")

            # 创建三个Frame，每个Frame包含一个标签和一个文本框
            frame_input_distance = tk.Frame(root_add_road)
            frame_input_distance.pack(padx=10, pady=5, anchor="n")
            frame_input_id1 = tk.Frame(root_add_road)
            frame_input_id1.pack(padx=10, pady=5, anchor="n")
            frame_input_id2 = tk.Frame(root_add_road)
            frame_input_id2.pack(padx=10, pady=5, anchor="n")

            lab_distance = tk.Label(frame_input_distance, text="道路距离:")
            entry_distance = tk.Entry(frame_input_distance)
            lab_id1 = tk.Label(frame_input_id1, text="第一个地点:")
            entry_id1 = tk.Entry(frame_input_id1)
            lab_id2 = tk.Label(frame_input_id2, text="第二个地点:")
            entry_id2 = tk.Entry(frame_input_id2)

            # 使用pack方法设置布局
            lab_distance.pack(side="left", padx=10, pady=5, anchor="w")
            entry_distance.pack(side="left", padx=10, pady=5, anchor="w")
            lab_id1.pack(side="left", padx=10, pady=5, anchor="w")
            entry_id1.pack(side="left", padx=10, pady=5, anchor="w")
            lab_id2.pack(side="left", padx=10, pady=5, anchor="w")
            entry_id2.pack(side="left", padx=10, pady=5, anchor="w")

            def button_click_ok():
                # 获取用户输入的值
                distance_value = entry_distance.get()
                id1_value = entry_id1.get()
                id2_value = entry_id2.get()

                # 数据验证需要做！！！！！！

                self.add_road(id1_value, id2_value, int(distance_value))
                self.print_all_nodes()

                self.draw_map(canvas)
                # root_add.destroy()
                # 最后一句可以不做 这样就可以连续添加

            # 创建两个按钮，一个确定，一个取消
            button_ok = tk.Button(root_add_road, text="确定", command=button_click_ok)
            button_cancel = tk.Button(root_add_road, text="取消", command=root_add_road.destroy)

            # 使用pack方法设置布局
            button_ok.pack(side=tk.LEFT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)
            button_cancel.pack(side=tk.RIGHT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)
            # 通过将 fill 设置为 tk.X，按钮会充满水平方向的可用空间。expand=True 则表示在有多余空间时扩展按钮以填充整个可用空间。

        def button_click_delete():
            root_delete = tk.Tk()
            root_delete.title("删除结点")
            root_delete.geometry("300x300")
            label_add = tk.Label(root_delete, text="请输入想要删除的结点：")
            label_add.pack(side=tk.TOP, padx=10, pady=5, anchor="n", fill="x")

            # 创建三个Frame，每个Frame包含一个标签和一个文本框
            frame_input_name = tk.Frame(root_delete)
            frame_input_name.pack(padx=10, pady=5, anchor="n")

            lab_name = tk.Label(frame_input_name, text="名称:")
            entry_name = tk.Entry(frame_input_name)

            # 使用pack方法设置布局
            lab_name.pack(side="left", padx=10, pady=5, anchor="w")
            entry_name.pack(side="left", padx=10, pady=5, anchor="w")

            def button_click_ok():
                # 获取用户输入的值
                name_value = entry_name.get()

                # 数据验证需要做！！！！！！

                self.remove_intersection(name_value)
                self.print_all_nodes()
                self.draw_map(canvas)
                # root_add.destroy()
                # 最后一句可以不做 这样就可以连续添加

            # 创建两个按钮，一个确定，一个取消
            button_ok = tk.Button(root_delete, text="确定", command=button_click_ok)
            button_cancel = tk.Button(root_delete, text="取消", command=root_delete.destroy)

            # 使用pack方法设置布局
            button_ok.pack(side=tk.LEFT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)
            button_cancel.pack(side=tk.RIGHT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)
            # 通过将 fill 设置为 tk.X，按钮会充满水平方向的可用空间。expand=True 则表示在有多余空间时扩展按钮以填充整个可用空间。

        def button_click_delete_road():
            root_delete_road = tk.Tk()
            root_delete_road.title("删除道路")
            root_delete_road.geometry("300x300")
            label_add = tk.Label(root_delete_road, text="请输入想要删除的道路：")
            label_add.pack(side=tk.TOP, padx=10, pady=5, anchor="n", fill="x")

            # 创建三个Frame，每个Frame包含一个标签和一个文本框
            frame_input_id1 = tk.Frame(root_delete_road)
            frame_input_id1.pack(padx=10, pady=5, anchor="n")
            frame_input_id2 = tk.Frame(root_delete_road)
            frame_input_id2.pack(padx=10, pady=5, anchor="n")

            lab_id1 = tk.Label(frame_input_id1, text="第一个地点:")
            entry_id1 = tk.Entry(frame_input_id1)
            lab_id2 = tk.Label(frame_input_id2, text="第二个地点:")
            entry_id2 = tk.Entry(frame_input_id2)

            # 使用pack方法设置布局
            lab_id1.pack(side="left", padx=10, pady=5, anchor="w")
            entry_id1.pack(side="left", padx=10, pady=5, anchor="w")
            lab_id2.pack(side="left", padx=10, pady=5, anchor="w")
            entry_id2.pack(side="left", padx=10, pady=5, anchor="w")

            def button_click_ok():
                # 获取用户输入的值
                id1_value = entry_id1.get()
                id2_value = entry_id2.get()

                self.remove_road(id1_value, id2_value)
                self.print_all_nodes()

                self.draw_map(canvas)
                # root_add.destroy()
                # 最后一句可以不做 这样就可以连续添加

            # 创建两个按钮，一个确定，一个取消
            button_ok = tk.Button(root_delete_road, text="确定", command=button_click_ok)
            button_cancel = tk.Button(root_delete_road, text="取消", command=root_delete_road.destroy)

            # 使用pack方法设置布局
            button_ok.pack(side=tk.LEFT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)
            button_cancel.pack(side=tk.RIGHT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)
            # 通过将 fill 设置为 tk.X，按钮会充满水平方向的可用空间。expand=True 则表示在有多余空间时扩展按钮以填充整个可用空间。

        def button_click_shortest():
            root_shortest = tk.Tk()
            root_shortest.title("最短路径")
            root_shortest.geometry("300x300")
            label_shortest = tk.Label(root_shortest, text="请输入两个结点的ID：")
            label_shortest.pack(side=tk.TOP, padx=10, pady=5, anchor="n", fill="x")

            # 创建两个Frame，每个Frame包含一个标签和一个文本框
            frame_input_start = tk.Frame(root_shortest)
            frame_input_start.pack(padx=10, pady=5, anchor="n")
            frame_input_end = tk.Frame(root_shortest)
            frame_input_end.pack(padx=10, pady=5, anchor="n")

            lab_start = tk.Label(frame_input_start, text="起始结点ID:")
            entry_start = tk.Entry(frame_input_start)
            lab_end = tk.Label(frame_input_end, text="目标结点ID:")
            entry_end = tk.Entry(frame_input_end)

            # 使用pack方法设置布局
            lab_start.pack(side="left", padx=10, pady=5, anchor="w")
            entry_start.pack(side="left", padx=10, pady=5, anchor="w")
            lab_end.pack(side="left", padx=10, pady=5, anchor="w")
            entry_end.pack(side="left", padx=10, pady=5, anchor="w")

            def button_click_ok():
                # 获取用户输入的值
                start_node_id = entry_start.get()
                end_node_id = entry_end.get()

                # 找到最短路径
                shortest_path_nodes = city_map.shortest_path_nodes(start_node_id, end_node_id)
                print(shortest_path_nodes)

                # 高亮（绿色）结点
                for node_id in shortest_path_nodes:
                    # 获取结点的坐标
                    x, y = city_map.graph[node_id]['coordinates']
                    x, y = x * var_x + var_add, y * var_x + var_add
                    r = draw_radius

                    # 使用canvas.create_oval的返回值来获取结点的ID
                    node_item = canvas.create_oval(x - r, y - r, x + r, y + r, fill="green", tags="node_text")

                    # 在结点旁边显示点的ID
                    canvas.create_text(x + r + 5, y, text=str(node_id), fill="black", anchor="w", tags="node_text")

                # 高亮（绿色）道路
                for i in range(len(shortest_path_nodes) - 1):
                    current_node = shortest_path_nodes[i]
                    next_node = shortest_path_nodes[i + 1]

                    # 获取当前结点和下一个结点的坐标
                    x_current, y_current = city_map.graph[current_node]['coordinates']
                    x_current, y_current = x_current * var_x + var_add, y_current * var_x + var_add
                    x_next, y_next = city_map.graph[next_node]['coordinates']
                    x_next, y_next = x_next * var_x + var_add, y_next * var_x + var_add

                    # 在边上显示权值
                    canvas.create_text((x_current + x_next) / 2, (y_current + y_next) / 2,
                                       text=str(city_map.graph[current_node]['roads'][next_node]), fill="black",
                                       tags="road_text")

                    # 将道路颜色修改为最短路径颜色
                    canvas.create_line(x_current, y_current, x_next, y_next, fill="green", tags="road")

                # 更新Canvas显示
                canvas.update()

            def button_click_cancle():
                canvas.delete("all")
                self.draw_map(canvas)
                root_shortest.destroy()

            # 创建两个按钮，一个确定，一个取消
            button_ok = tk.Button(root_shortest, text="确定", command=button_click_ok)
            button_cancel = tk.Button(root_shortest, text="取消", command=button_click_cancle)
            # 使用pack方法设置布局
            button_ok.pack(side=tk.LEFT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)
            button_cancel.pack(side=tk.RIGHT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)

        def button_click_find():
            root_find = tk.Tk()
            root_find.title("查找点以及周围点")
            root_find.geometry("300x300")
            label_shortest = tk.Label(root_find, text="请输入查找结点的ID：")
            label_shortest.pack(side=tk.TOP, padx=10, pady=5, anchor="n", fill="x")

            # 创建两个Frame，每个Frame包含一个标签和一个文本框
            frame_input_id = tk.Frame(root_find)
            frame_input_id.pack(padx=10, pady=5, anchor="n")

            lab_id = tk.Label(frame_input_id, text="结点ID:")
            entry_id = tk.Entry(frame_input_id)

            # 使用pack方法设置布局
            lab_id.pack(side="left", padx=10, pady=5, anchor="w")
            entry_id.pack(side="left", padx=10, pady=5, anchor="w")

            def button_click_ok():
                # 获取用户输入的值
                find_id = entry_id.get()

                # 数据验证

                # 找到最短路径
                near_id = self.adjacent_intersections(find_id)
                print(near_id)

                x, y = city_map.graph[find_id]['coordinates']
                x, y = x * var_x + var_add, y * var_x + var_add
                r = draw_radius
                # 使用canvas.create_oval的返回值来获取结点的ID
                node_item = canvas.create_oval(x - r, y - r, x + r, y + r, fill="red", tags="node_text")
                # 在结点旁边显示点的ID
                canvas.create_text(x + r + 5, y, text=str(find_id), fill="black", anchor="w", tags="node_text")

                # 高亮（绿色）结点
                for node_id in near_id:
                    # 获取结点的坐标
                    x, y = city_map.graph[node_id]['coordinates']
                    x, y = x * var_x + var_add, y * var_x + var_add
                    r = draw_radius

                    # 使用canvas.create_oval的返回值来获取结点的ID
                    node_item = canvas.create_oval(x - r, y - r, x + r, y + r, fill="yellow", tags="node_text")

                    # 在结点旁边显示点的ID
                    canvas.create_text(x + r + 5, y, text=str(node_id), fill="black", anchor="w", tags="node_text")

                # 更新Canvas显示
                canvas.update()

            def button_click_cancle():
                canvas.delete("all")
                self.draw_map(canvas)
                root_find.destroy()

            # 创建两个按钮，一个确定，一个取消
            button_ok = tk.Button(root_find, text="确定", command=button_click_ok)
            button_cancel = tk.Button(root_find, text="取消", command=button_click_cancle)
            # 使用pack方法设置布局
            button_ok.pack(side=tk.LEFT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)
            button_cancel.pack(side=tk.RIGHT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)

        def button_click_eg1():
            """第一个例子，取自实验中的图"""
            self.init_1()
            self.print_all_nodes()
            self.draw_map(canvas)

        def button_click_eg2():
            """第二个例子，取自学校结点"""
            self.init_2()
            self.print_all_nodes()
            self.draw_map(canvas)

        def button_click_flow():
            root_flow = tk.Tk()
            root_flow.title("流量测试")
            root_flow.geometry("300x300")

            frame_input_id = tk.Frame(root_flow)
            frame_input_id.pack(padx=10, pady=5, anchor="n")

            lab_flow = tk.Label(frame_input_id, text="请输入仿真次数：")
            entry_flow = tk.Entry(frame_input_id)

            lab_flow.pack(side="left", padx=10, pady=5, anchor="w")
            entry_flow.pack(side="left", padx=10, pady=5, anchor="w")

            def button_click_ok():
                # 获取用户输入的值
                find_flow = entry_flow.get()
                self.car_Flow(int(find_flow))
                self.print_all_nodes()
                # 以列表显示在root_flow上，并且大的在上面

                # 显示每个ID的流量，按照流量从大到小排序
                sorted_nodes = sorted(self.graph.items(), key=lambda x: x[1]['flow'], reverse=True)

                # 创建 Listbox
                listbox = tk.Listbox(root_flow)
                listbox.pack(side=tk.TOP)

                for (node_id, node_info) in sorted_nodes:
                    # 添加每个ID的流量到 Listbox
                    listbox.insert(tk.END, f"{node_id}        \t{str(node_info['flow'])}")
                    # rjust(10) 是一个字符串方法，它在字符串的左侧填充足够的空格，使得整个字符串达到指定的宽度。在这个例子中，宽度是10个字符。

            def button_click_cancle():
                # 流量清零
                for node_id in self.graph:
                    self.graph[node_id]['flow'] = 0
                self.print_all_nodes()
                root_flow.destroy()

            # 创建两个按钮，一个确定，一个取消
            button_ok = tk.Button(root_flow, text="确定", command=button_click_ok)
            button_cancel = tk.Button(root_flow, text="取消", command=button_click_cancle)
            # 使用pack方法设置布局
            button_ok.pack(side=tk.LEFT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)
            button_cancel.pack(side=tk.RIGHT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)

        def button_click_clear():
            self.graph = {}
            self.draw_map(canvas)

        def zoom_in():
            canvas.scale("all", 0, 0, 1.2, 1.2)

        def zoom_out():
            canvas.scale("all", 0, 0, 0.8, 0.8)

        def button_click_help():
            root_help = tk.Tk()
            root_help.title("帮助")
            root_help.geometry("300x300")

            frame_input_id = tk.Frame(root_help)
            frame_input_id.pack(padx=10, pady=5, anchor="n")

            text = "此项目是21电子信息工程数据结构课设内容\n小组成员：颜天煜 王海博 田延翔 张家璇\n运行示例2需要cumt_data2.xlsx在" \
                   "同一目录下\n代码还有部分小bug 欢迎大家开发与讨论\n开发者联系方式：752971750@qq.com\n代码已在Github上开源"

            lab_flow = tk.Label(frame_input_id, text=text)
            lab_flow.pack(side="left", padx=10, pady=5, anchor="w")

            def button_click_ok():
                webbrowser.open("https://github.com/CUMT-Yantianyu/CUMT-Work")

            def button_click_cancle():
                root_help.destroy()

            # 创建两个按钮，一个确定，一个取消
            button_ok = tk.Button(root_help, text="查看源码", command=button_click_ok)
            button_cancel = tk.Button(root_help, text="取消", command=button_click_cancle)
            # 使用pack方法设置布局
            button_ok.pack(side=tk.LEFT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)
            button_cancel.pack(side=tk.RIGHT, padx=20, pady=20, anchor="s", fill=tk.X, expand=True)

        button_frame = tk.Frame(root)
        button_frame.pack(side=tk.LEFT, padx=10, pady=5, anchor="n", fill="y")

        label = tk.Label(root, text="中国矿业大学21电子信息工程数据结构课设\n颜天煜 王海博 张家璇 田延翔\n点击按钮以操作")
        label.pack(side=tk.TOP, pady=10)

        button_add = tk.Button(button_frame, text="增加结点", command=button_click_add)
        button_add.pack(side=tk.TOP, padx=10, pady=5, anchor="w", fill="x")
        button_add_road = tk.Button(button_frame, text="添加道路", command=button_click_add_road)
        button_add_road.pack(side=tk.TOP, padx=10, pady=5, anchor="w", fill="x")
        button_delete = tk.Button(button_frame, text="删除结点", command=button_click_delete)
        button_delete.pack(side=tk.TOP, padx=10, pady=5, anchor="w", fill="x")
        button_delete_road = tk.Button(button_frame, text="删除道路", command=button_click_delete_road)
        button_delete_road.pack(side=tk.TOP, padx=10, pady=5, anchor="w", fill="x")
        button_shortest = tk.Button(button_frame, text="最短路径", command=button_click_shortest)
        button_shortest.pack(side=tk.TOP, padx=10, pady=5, anchor="w", fill="x")
        button_find = tk.Button(button_frame, text="查找结点", command=button_click_find)
        button_find.pack(side=tk.TOP, padx=10, pady=5, anchor="w", fill="x")
        button_eg1 = tk.Button(button_frame, text="示例1：实验地图", command=button_click_eg1)
        button_eg1.pack(side=tk.TOP, padx=10, pady=5, anchor="w", fill="x")
        button_eg2 = tk.Button(button_frame, text="示例2：学校地图", command=button_click_eg2)
        button_eg2.pack(side=tk.TOP, padx=10, pady=5, anchor="w", fill="x")
        button_flow = tk.Button(button_frame, text="流量仿真", command=button_click_flow)
        button_flow.pack(side=tk.TOP, padx=10, pady=5, anchor="w", fill="x")
        button_clear = tk.Button(button_frame, text="清屏", command=button_click_clear)
        button_clear.pack(side=tk.TOP, padx=10, pady=5, anchor="w", fill="x")
        button_zoom_in = tk.Button(button_frame, text="放大", command=zoom_in)
        button_zoom_in.pack(side=tk.TOP, padx=10, pady=5, anchor="w", fill="x")
        button_zoom_out = tk.Button(button_frame, text="缩小", command=zoom_out)
        button_zoom_out.pack(side=tk.TOP, padx=10, pady=5, anchor="w", fill="x")
        button_help = tk.Button(button_frame, text="帮助", command=button_click_help)
        button_help.pack(side=tk.BOTTOM, padx=10, pady=5, anchor="w", fill="x")

        canvas = tk.Canvas(root, bg="white")
        canvas.config(width=800, height=800)
        canvas.pack(side=tk.LEFT)  # 将画布放置在左侧

        root.mainloop()


# 示例用法
city_map = CityMap()

# 显示地图的GUI界面
city_map.display_map_gui()
