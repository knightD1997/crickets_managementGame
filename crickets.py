import tkinter as tk
from tkinter import ttk, messagebox, PhotoImage
from PIL import Image, ImageTk
import json
import os

CRICKET_FILE = "crickets.json"


def save_cricket_to_file(cricket_dict):
    crickets = []
    if os.path.exists(CRICKET_FILE):
        with open(CRICKET_FILE, "r") as file:
            crickets = json.load(file)
    crickets.append(cricket_dict)
    with open(CRICKET_FILE, "w") as file:
        json.dump(crickets, file)


def read_crickets_from_file():
    if not os.path.exists(CRICKET_FILE):
        return []
    with open(CRICKET_FILE, "r") as file:
        return json.load(file)


def remove_cricket_from_file(cricket_name):
    if not os.path.exists(CRICKET_FILE):
        return
    with open(CRICKET_FILE, "r") as file:
        crickets = json.load(file)
    crickets = [cricket for cricket in crickets if cricket["name"] != cricket_name]
    with open(CRICKET_FILE, "w") as file:
        json.dump(crickets, file)


class CricketApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("蟋蟀管理界面")
        self.geometry("1350x700")
        self.current_editing_cricket = None
        self.init_ui()

    def init_ui(self):
        self.entry_frame = ttk.Frame(self)
        self.entry_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nw")

        # 输入字段：名称、品种、等级、体型
        ttk.Label(self.entry_frame, text="名称").grid(row=0, column=0)
        self.name_var = tk.StringVar()
        ttk.Entry(self.entry_frame, textvariable=self.name_var).grid(
            row=0, column=1, columnspan=2
        )

        ttk.Label(self.entry_frame, text="品种").grid(row=1, column=0)
        self.breed_var = tk.StringVar()
        ttk.Entry(self.entry_frame, textvariable=self.breed_var).grid(
            row=1, column=1, columnspan=2
        )

        ttk.Label(self.entry_frame, text="等级").grid(row=2, column=0)
        self.level_var = tk.StringVar()
        ttk.Combobox(
            self.entry_frame,
            textvariable=self.level_var,
            values=[str(i) for i in range(1, 16)],
            state="readonly",
        ).grid(row=2, column=1, columnspan=2)

        ttk.Label(self.entry_frame, text="体型").grid(row=3, column=0)
        self.size_var = tk.StringVar()
        ttk.Combobox(
            self.entry_frame,
            textvariable=self.size_var,
            values=["小", "中", "大"],
            state="readonly",
        ).grid(row=3, column=1, columnspan=2)

        # 属性输入：八大属性的区分和等级
        self.attr_vars = {}
        self.attr_levels = {}
        row = 4
        for attr in ["攻击", "防御", "斗性", "体力", "暴击", "命中", "格挡", "攻速"]:
            ttk.Label(self.entry_frame, text=attr).grid(row=row, column=0)
            self.attr_vars[attr] = tk.StringVar()
            combobox_attr = ttk.Combobox(
                self.entry_frame,
                textvariable=self.attr_vars[attr],
                values=["低", "中", "高", "超", "神"],
                state="readonly",
            )
            combobox_attr.grid(row=row, column=1)
            combobox_attr.bind(
                "<<ComboboxSelected>>", lambda event, a=attr: self.update_attr_level(a)
            )

            self.attr_levels[attr] = tk.StringVar()
            combobox_level = ttk.Combobox(
                self.entry_frame, textvariable=self.attr_levels[attr], state="readonly"
            )
            combobox_level.grid(row=row, column=2)
            row += 1

        ttk.Button(
            self.entry_frame, text="添加/更新蟋蟀", command=self.add_or_update_cricket
        ).grid(row=row, column=0, columnspan=3, pady=5)
        row += 1
        ttk.Button(
            self.entry_frame, text="展示蟋蟀信息", command=self.display_crickets
        ).grid(row=row, column=0, columnspan=3, pady=5)

        row += 1
        self.insert_cover_image(row)

        self.display_area = ttk.Notebook(self)
        self.display_area.grid(
            row=0, column=1, padx=10, pady=10, sticky="nswe", columnspan=2
        )
        self.size_frames = {
            "小": ttk.Frame(self.display_area),
            "中": ttk.Frame(self.display_area),
            "大": ttk.Frame(self.display_area),
        }
        for size, frame in self.size_frames.items():
            self.display_area.add(frame, text=f"{size}体型蟋蟀")

    def insert_cover_image(self, row):
        # 使用Pillow调整图像大小
        original_image = Image.open("cover.jpg")
        resized_image = original_image.resize(
            (300, 300), Image.ANTIALIAS
        )  # 根据需要调整尺寸
        self.cover_image = ImageTk.PhotoImage(resized_image)

        cover_label = ttk.Label(self.entry_frame, image=self.cover_image)
        cover_label.grid(row=row, column=0, columnspan=3, pady=20)

    def fill_cricket_info_for_edit(self, cricket):
        self.current_editing_cricket = cricket
        self.name_var.set(cricket["name"])
        self.breed_var.set(cricket["breed"])
        self.level_var.set(cricket["level"])
        self.size_var.set(cricket["size"])

        for attr, var in self.attr_vars.items():
            # 假设cricket["attributes"][attr]直接存储了属性值
            attr_value = cricket["attributes"].get(attr, "")
            self.attr_levels[attr].set(attr_value)  # 具体属性值填入第二个属性框

            # 根据具体属性值确定属性区分并更新第一个属性框
            attr_category = self.determine_attribute_category(attr_value)
            var.set(attr_category)

    def determine_attribute_category(self, value):
        # 此函数用于根据属性值确定属性区分
        try:
            value = int(value)
            if 1 <= value <= 3:
                return "低"
            elif 4 <= value <= 6:
                return "中"
            elif 7 <= value <= 9:
                return "高"
            elif value == 10:
                return "超"
            elif value == 11:
                return "神"
        except ValueError:
            # 如果值不是整数，尝试解析为区间
            if "-" in value:
                lower, upper = map(int, value.split("-"))
                if 1 <= lower <= 3:
                    return "低"
                elif 4 <= lower <= 6:
                    return "中"
                elif 7 <= lower <= 9:
                    return "高"
        return ""  # 默认返回空字符串，表示未知区分


    def determine_attribute_value(self, category, value):
        """根据属性区分和具体值确定最终保存的属性信息"""
        category_to_value = {
            "低": "1-3",
            "中": "4-6",
            "高": "7-9",
            "超": "10",
            "神": "11",
        }
        # 如果用户直接输入了具体数值或区间，且这个值与区分对应的默认值不同，则直接使用用户输入的值
        if value not in category_to_value.values():
            return value  # 用户输入了具体的数值或自定义区间
        else:
            return category_to_value.get(category, "")  # 使用区分对应的默认值

    def add_or_update_cricket(self):
        """添加或更新蟋蟀信息"""
        cricket_dict = {
            "name": self.name_var.get(),
            "breed": self.breed_var.get(),
            "level": self.level_var.get(),
            "size": self.size_var.get(),
            "attributes": {},
        }
        for attr in self.attr_vars:
            # 假设我们已经根据属性区分和具体值确定了如何保存这些信息
            attr_value = self.determine_attribute_value(
                self.attr_vars[attr].get(), self.attr_levels[attr].get()
            )
            cricket_dict["attributes"][attr] = attr_value

        if self.current_editing_cricket:
            # 找到并更新原有蟋蟀信息
            crickets = read_crickets_from_file()
            for i, cricket in enumerate(crickets):
                if cricket["name"] == self.current_editing_cricket["name"]:
                    crickets[i] = cricket_dict
                    break
        else:
            # 添加新的蟋蟀信息
            crickets.append(cricket_dict)

        with open(CRICKET_FILE, "w") as file:
            json.dump(crickets, file)

        self.clear_input_fields()
        self.display_crickets()
        self.current_editing_cricket = None  # 重置正在编辑的蟋蟀信息

    def update_attr_level(self, attr):
        attr_selection = self.attr_vars[attr].get()
        level_combobox = self.entry_frame.grid_slaves(
            row=4 + list(self.attr_vars.keys()).index(attr), column=2
        )[0]
        level_options, default_option = self.get_level_options(attr_selection)
        level_combobox.configure(values=level_options)
        self.attr_levels[attr].set(default_option)

    def get_level_options(self, selection):
        options = {
            "低": ([1, 2, 3, "1-2", "2-3", "1-3"], "1-3"),
            "中": ([4, 5, 6, "4-5", "5-6", "4-6"], "4-6"),
            "高": ([7, 8, 9, "7-8", "8-9", "7-9"], "7-9"),
            "超": ([10], "10"),
            "神": ([11], "11"),
        }
        return options.get(selection, ([], ""))

    def clear_input_fields(self):
        self.name_var.set("")
        self.breed_var.set("")
        self.level_var.set("")
        self.size_var.set("")
        for var in self.attr_vars.values():
            var.set("")
        for var in self.attr_levels.values():
            var.set("")

    def get_attribute_color(self, value):
        """根据属性值返回对应的颜色的六进制码"""
        if value in ["低", "1-2", "2-3", "1-3", "1", "2", "3"]:
            return "#870007"  # 红色
        elif value in ["中", "4-5", "5-6", "4-6", "4", "5", "6"]:
            return "#000000"  # 黑色，默认颜色
        elif value in ["高", "7-8", "8-9", "7-9", "7", "8", "9"]:
            return "#008000"  # 绿色
        elif value == "10":
            return "#11c6f9"  # 蓝色
        elif value == "11":
            return "#FFA500"  # 橙色
        else:
            return "#000000"  # 对于未知的值，使用默认颜色（黑色）

    def display_crickets(self):
        for frame in self.size_frames.values():
            for widget in frame.winfo_children():
                widget.destroy()

        crickets = read_crickets_from_file()
        for cricket in crickets:
            frame = self.size_frames.get(
                cricket["size"], self.size_frames["小"]
            )  # 默认到“小”标签页，如果未找到对应的体型
            cricket_frame = ttk.Frame(frame, padding=5)
            cricket_frame.pack(fill=tk.X, padx=5, pady=5)

            ttk.Label(cricket_frame, text=cricket["name"], width=8).pack(side=tk.LEFT)
            ttk.Label(cricket_frame, text=cricket["breed"], width=10).pack(side=tk.LEFT)
            ttk.Label(cricket_frame, text=f"Level: {cricket['level']}", width=12).pack(
                side=tk.LEFT
            )
            for k, v in cricket["attributes"].items():
                attr_color = self.get_attribute_color(v)
                ttk.Label(
                    cricket_frame, text=f"{k}: {v}", foreground=attr_color, width=10
                ).pack(side=tk.LEFT)

            ttk.Button(
                cricket_frame,
                text="🔄",
                command=lambda cricket=cricket: self.fill_cricket_info_for_edit(
                    cricket
                ),
                width=2,
            ).pack(side=tk.LEFT)
            ttk.Button(
                cricket_frame,
                text="↑",
                command=lambda name=cricket["name"]: self.move_cricket(name, "up"),
                width=2,
            ).pack(side=tk.LEFT)
            ttk.Button(
                cricket_frame,
                text="↓",
                command=lambda name=cricket["name"]: self.move_cricket(name, "down"),
                width=2,
            ).pack(side=tk.LEFT)
            ttk.Button(
                cricket_frame,
                text="✖",
                command=lambda name=cricket["name"]: self.delete_cricket(name),
                width=2,
            ).pack(side=tk.RIGHT)

    def move_cricket(self, cricket_name, direction):
        crickets = read_crickets_from_file()
        index = next(
            (
                i
                for i, cricket in enumerate(crickets)
                if cricket["name"] == cricket_name
            ),
            None,
        )

        if index is not None:
            if direction == "up" and index > 0:
                crickets[index], crickets[index - 1] = (
                    crickets[index - 1],
                    crickets[index],
                )
            elif direction == "down" and index < len(crickets) - 1:
                crickets[index], crickets[index + 1] = (
                    crickets[index + 1],
                    crickets[index],
                )

            with open(CRICKET_FILE, "w") as file:
                json.dump(crickets, file)

            self.display_crickets()

    def delete_cricket(self, cricket_name):
        remove_cricket_from_file(cricket_name)
        self.display_crickets()


if __name__ == "__main__":
    app = CricketApp()
    app.mainloop()
