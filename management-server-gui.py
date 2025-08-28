import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
import json
import asyncio
import websockets
import threading
import logging
import colorlog
from datetime import datetime

# 配置日志
colorlog.basicConfig(
    format='%(log_color)s[%(asctime)s %(levelname)s]\t %(message)s',
    level=logging.DEBUG,
    log_colors={
        'DEBUG': 'green',
        'INFO': 'cyan',
        'WARNING': 'yellow',
        'ERROR': 'red',
        'CRITICAL': 'red,bg_white',
    }
)
logger = logging.getLogger(__name__)

# 从提供的discover.json中提取的方法数据
with open('discover.json', 'r') as f:
    discover_data = json.load(f)

methods = discover_data['result']['methods']
schemas = discover_data['result']['components']['schemas']

class MinecraftRPCClient:
    def __init__(self, host='localhost', port=25585):
        self.host = host
        self.port = port
        self.websocket = None
        self.connected = False
        self.request_id = 1
        self.loop = None
        self.thread = None
        
    def start_loop(self):
        """启动事件循环的线程"""
        self.loop = asyncio.new_event_loop()
        self.thread = threading.Thread(target=self._run_loop, daemon=True)
        self.thread.start()
        
    def _run_loop(self):
        """运行事件循环"""
        asyncio.set_event_loop(self.loop)
        self.loop.run_forever()
        
    async def _connect(self):
        """内部连接方法"""
        try:
            self.websocket = await websockets.connect(f"ws://{self.host}:{self.port}")
            self.connected = True
            logger.info(f"Connected to Minecraft server at {self.host}:{self.port}")
            return True
        except Exception as e:
            logger.error(f"Connection failed: {e}")
            return False
            
    def connect(self):
        """连接服务器"""
        if not self.loop:
            self.start_loop()
            
        future = asyncio.run_coroutine_threadsafe(self._connect(), self.loop)
        return future.result()
            
    async def _disconnect(self):
        """内部断开连接方法"""
        if self.websocket:
            await self.websocket.close()
            self.connected = False
            logger.info("Disconnected from Minecraft server")
            
    def disconnect(self):
        """断开连接"""
        if self.loop and self.loop.is_running():
            future = asyncio.run_coroutine_threadsafe(self._disconnect(), self.loop)
            future.result()
            
    async def _call_method(self, method, params=None):
        """内部方法调用"""
        if not self.connected:
            if not await self._connect():
                return None
                
        request = {
            "jsonrpc": "2.0",
            "id": self.request_id,
            "method": method,
        }
        
        if params:
            request["params"] = params
            
        self.request_id += 1
        
        try:
            await self.websocket.send(json.dumps(request))
            response = await self.websocket.recv()
            return json.loads(response)
        except Exception as e:
            logger.error(f"Method call failed: {e}")
            return None
            
    def call_method(self, method, params=None):
        """调用方法"""
        if not self.loop or not self.loop.is_running():
            self.start_loop()
            
        future = asyncio.run_coroutine_threadsafe(self._call_method(method, params), self.loop)
        return future.result()

class MethodDialog(tk.Toplevel):
    def __init__(self, parent, method, client):
        super().__init__(parent)
        self.method = method
        self.client = client
        self.parent_app = parent  # 保存父应用引用
        self.title(f"Execute: {method['name']}")
        self.geometry("500x400")
        self.result = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # 方法描述
        desc_frame = ttk.LabelFrame(self, text="Description")
        desc_frame.pack(fill="x", padx=10, pady=5)
        
        desc_label = ttk.Label(desc_frame, text=self.method['description'], wraplength=450)
        desc_label.pack(padx=5, pady=5)
        
        # 参数输入区域
        if self.method.get('params'):
            params_frame = ttk.LabelFrame(self, text="Parameters")
            params_frame.pack(fill="both", expand=True, padx=10, pady=5)
            
            self.param_vars = {}
            for i, param in enumerate(self.method['params']):
                param_frame = ttk.Frame(params_frame)
                param_frame.pack(fill="x", padx=5, pady=2)
                
                ttk.Label(param_frame, text=f"{param['name']}:").pack(side="left")
                
                # 根据参数类型创建不同的输入控件
                schema = param['schema']
                if schema.get('type') == 'boolean':
                    var = tk.BooleanVar()
                    ttk.Checkbutton(param_frame, variable=var).pack(side="left")
                elif schema.get('type') == 'integer':
                    var = tk.StringVar()
                    ttk.Entry(param_frame, textvariable=var).pack(side="left", fill="x", expand=True)
                elif schema.get('type') == 'string':
                    var = tk.StringVar()
                    ttk.Entry(param_frame, textvariable=var).pack(side="left", fill="x", expand=True)
                elif schema.get('type') == 'array':
                    var = tk.StringVar()
                    ttk.Label(param_frame, text="[Array - enter as JSON]").pack(side="left")
                    ttk.Entry(param_frame, textvariable=var).pack(side="left", fill="x", expand=True)
                else:
                    var = tk.StringVar()
                    ttk.Entry(param_frame, textvariable=var).pack(side="left", fill="x", expand=True)
                
                self.param_vars[param['name']] = var
        else:
            no_params_label = ttk.Label(self, text="This method has no parameters")
            no_params_label.pack(pady=10)
            
        # 按钮区域
        button_frame = ttk.Frame(self)
        button_frame.pack(fill="x", padx=10, pady=10)
        
        ttk.Button(button_frame, text="Execute", command=self.execute).pack(side="right", padx=5)
        ttk.Button(button_frame, text="Cancel", command=self.destroy).pack(side="right", padx=5)
        
    def execute(self):
        # 构建参数
        params = []
        if self.method.get('params'):
            for param in self.method['params']:
                var = self.param_vars[param['name']]
                value = var.get()
                
                # 尝试解析JSON格式的输入
                if param['schema'].get('type') == 'array' and value:
                    try:
                        value = json.loads(value)
                    except json.JSONDecodeError:
                        messagebox.showerror("Error", f"Invalid JSON format for parameter {param['name']}")
                        return
                
                # 转换类型
                if param['schema'].get('type') == 'integer' and value:
                    try:
                        value = int(value)
                    except ValueError:
                        messagebox.showerror("Error", f"Invalid integer value for parameter {param['name']}")
                        return
                elif param['schema'].get('type') == 'boolean':
                    value = bool(value)
                
                params.append(value)
        
        # 执行方法调用
        try:
            result = self.client.call_method(self.method['name'], params if params else None)
            self.parent_app.log_response(self.method['name'], result)
        except Exception as e:
            logger.error(f"Error executing method: {e}")
            messagebox.showerror("Error", f"Failed to execute method: {e}")
                
        self.destroy()

class MinecraftRPCApp(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.title("Minecraft Server JSON-RPC Controller")
        self.geometry("800x600")
        
        self.client = MinecraftRPCClient()
        
        self.create_widgets()
        
        # 尝试连接服务器
        self.after(100, self.connect_to_server)
        
    def create_widgets(self):
        # 主框架
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 方法列表
        method_frame = ttk.LabelFrame(main_frame, text="Available Methods")
        method_frame.pack(fill="both", expand=True, pady=(0, 10))
        
        # 创建树形视图显示方法
        self.method_tree = ttk.Treeview(method_frame, columns=("description"), show="tree headings")
        self.method_tree.heading("#0", text="Name")
        self.method_tree.heading("description", text="Description")
        self.method_tree.column("#0", width=300)
        self.method_tree.column("description", width=400)
        
        # 添加滚动条
        scrollbar = ttk.Scrollbar(method_frame, orient="vertical", command=self.method_tree.yview)
        self.method_tree.configure(yscrollcommand=scrollbar.set)
        
        self.method_tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 绑定双击事件
        self.method_tree.bind("<Double-1>", self.on_method_double_click)
        
        # 日志输出
        log_frame = ttk.LabelFrame(main_frame, text="Log")
        log_frame.pack(fill="both", expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, width=80, height=15)
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        self.log_text.configure(state="disabled")
        
        # 状态栏
        self.status_var = tk.StringVar()
        self.status_var.set("Disconnected")
        status_bar = ttk.Label(self, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(side="bottom", fill="x")
        
        # 填充方法树
        self.populate_method_tree()
        
    def populate_method_tree(self):
        # 按命名空间组织方法
        namespaces = {}
        
        for method in methods:
            if 'name' in method and 'description' in method:
                # 跳过通知方法
                if method['name'].startswith('notification:'):
                    continue
                    
                namespace = method['name'].split(':')[0]
                if namespace not in namespaces:
                    namespaces[namespace] = []
                namespaces[namespace].append(method)
        
        # 添加到树形视图
        for namespace, method_list in namespaces.items():
            namespace_node = self.method_tree.insert("", "end", text=namespace, values=(""))
            
            for method in method_list:
                self.method_tree.insert(
                    namespace_node, "end", 
                    text=method['name'], 
                    values=(method['description'])
                )
        
        # 展开所有节点
        for namespace in namespaces.keys():
            node_id = self.method_tree.get_children()[list(namespaces.keys()).index(namespace)]
            self.method_tree.item(node_id, open=True)
    
    def on_method_double_click(self, event):
        item = self.method_tree.selection()[0]
        item_text = self.method_tree.item(item, "text")
        
        # 查找对应的方法
        for method in methods:
            if method['name'] == item_text:
                MethodDialog(self, method, self.client)
                break
    
    def log_response(self, method_name, response):
        self.log_text.configure(state="normal")
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        if response:
            self.log_text.insert("end", f"[{timestamp}] {method_name}:\n")
            self.log_text.insert("end", json.dumps(response, indent=2) + "\n\n")
        else:
            self.log_text.insert("end", f"[{timestamp}] {method_name}: ERROR - No response received\n\n")
            
        self.log_text.see("end")
        self.log_text.configure(state="disabled")
    
    def connect_to_server(self):
        try:
            connected = self.client.connect()
            if connected:
                self.status_var.set("Connected to Minecraft server")
            else:
                self.status_var.set("Connection failed")
        except Exception as e:
            logger.error(f"Connection error: {e}")
            self.status_var.set("Connection error")
                
    def __del__(self):
        if hasattr(self, 'client'):
            self.client.disconnect()

if __name__ == "__main__":
    app = MinecraftRPCApp()
    app.mainloop()