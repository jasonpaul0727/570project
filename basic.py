import time
import sys

# 尝试导入 resource，如果是在 Windows 上失败，则忽略错误
try:
    import resource
except ImportError:
    resource = None  # Windows 环境下标记为 None

# 如果你想在 Windows 上也能看到真实的内存数值，可以使用 psutil 库 (可选)
# 你需要在终端运行: pip install psutil
try:
    import psutil
except ImportError:
    psutil = None

class InputGenerator:
    def __init__(self, filepath):
        self.filepath = filepath

    def generate(self):
        with open(self.filepath, 'r') as f:
            lines = [line.strip() for line in f.readlines()]

        # 解析第一个字符串
        base_s1 = lines[0]
        indices_s1 = []
        current_idx = 1

        # 读取数字直到遇到非数字（即第二个基字符串）
        while current_idx < len(lines):
            if lines[current_idx].isdigit():
                indices_s1.append(int(lines[current_idx]))
                current_idx += 1
            else:
                break

        # 解析第二个字符串
        base_s2 = lines[current_idx]
        indices_s2 = []
        current_idx += 1
        while current_idx < len(lines):
            if lines[current_idx].isdigit():
                indices_s2.append(int(lines[current_idx]))
                current_idx += 1
            else:
                break

        return self._process_string(base_s1, indices_s1), self._process_string(base_s2, indices_s2)

    def _process_string(self, base_str, indices):
        """
        Task A: 迭代生成字符串
        Step k: insert copy of s within itself right after index n
        """
        s = base_str
        for idx in indices:
            # s[:idx+1] 包含了索引 idx 及其左边的字符
            s = s[:idx + 1] + s + s[idx + 1:]
        return s

class BasicSolver:
    def __init__(self):
        # 初始化惩罚常数 [cite: 56, 57]
        self.DELTA = 30
        self.ALPHA = {
            'A': {'A': 0, 'C': 110, 'G': 48, 'T': 94},
            'C': {'A': 110, 'C': 0, 'G': 118, 'T': 48},
            'G': {'A': 48, 'C': 118, 'G': 0, 'T': 110},
            'T': {'A': 94, 'C': 48, 'G': 110, 'T': 0}
        }

    def solve(self, s1, s2):
        m, n = len(s1), len(s2)

        # 1. 初始化 DP 表格 (m+1) x (n+1)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        # 2. 初始化边界
        for i in range(1, m + 1):
            dp[i][0] = i * self.DELTA
        for j in range(1, n + 1):
            dp[0][j] = j * self.DELTA

        # 3. 填表 (Recurrence)
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                char1 = s1[i - 1]
                char2 = s2[j - 1]

                cost_match = dp[i - 1][j - 1] + self.ALPHA[char1][char2]
                cost_gap1 = dp[i - 1][j] + self.DELTA
                cost_gap2 = dp[i][j - 1] + self.DELTA

                dp[i][j] = min(cost_match, cost_gap1, cost_gap2)

        # 4. 回溯 (Backtracking)
        align1 = []
        align2 = []
        i, j = m, n

        while i > 0 or j > 0:
            char1 = s1[i - 1] if i > 0 else None
            char2 = s2[j - 1] if j > 0 else None

            current_score = dp[i][j]

            # 优先检查是否来自匹配/错配 (对角线)
            if i > 0 and j > 0 and current_score == dp[i - 1][j - 1] + self.ALPHA[char1][char2]:
                align1.append(char1)
                align2.append(char2)
                i -= 1
                j -= 1
            # 检查是否来自 s1 的 gap (上方)
            elif i > 0 and current_score == dp[i - 1][j] + self.DELTA:
                align1.append(char1)
                align2.append('_')
                i -= 1
            # 检查是否来自 s2 的 gap (左方)
            else:
                align1.append('_')
                align2.append(char2)
                j -= 1

        # 结果是反向生成的，需要翻转
        return dp[m][n], "".join(align1[::-1]), "".join(align2[::-1])

def process_memory():
    # 优先使用 resource (Linux/提交环境标准)
    if resource:
        usage = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        # Linux 这里的单位通常是 KB
        return usage

    # 如果是 Windows 开发环境，使用 psutil (如果有的话)
    elif psutil:
        process = psutil.Process()
        memory_info = process.memory_info()
        # psutil 返回的是字节 (Bytes)，题目要求 KB，所以除以 1024
        return int(memory_info.rss / 1024)

    # 如果都没有 (Windows 且没装 psutil)，返回 0 防止报错
    else:
        return 0

def measure_performance():
    # 处理命令行参数
    if len(sys.argv) < 3:
        input_path = 'input.txt'
        output_path = 'output.txt'
        print(f"【提示】未检测到命令行参数，使用默认文件：输入={input_path}, 输出={output_path}")
    else:
        input_path = sys.argv[1]
        output_path = sys.argv[2]

    # 生成字符串
    generator = InputGenerator(input_path)
    s1, s2 = generator.generate()

    solver = BasicSolver()

    # 记录开始时间
    start_time = time.time()

    # 运行算法
    cost, align1, align2 = solver.solve(s1, s2)

    # 记录结束时间
    end_time = time.time()
    time_taken_ms = (end_time - start_time) * 1000

    # 获取内存
    memory_kb = process_memory()

    # 写入文件
    with open(output_path, 'w') as f:
        f.write(f"{cost}\n")
        f.write(f"{align1}\n")
        f.write(f"{align2}\n")
        f.write(f"{time_taken_ms}\n")
        f.write(f"{memory_kb}\n")

# 这是一个非常关键的部分，之前你的代码里可能没有这行，导致程序什么都不做就退出了
if __name__ == "__main__":
    measure_performance()