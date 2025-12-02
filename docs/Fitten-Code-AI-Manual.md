# Fitten Code AI 编程助手 使用手册

## 产品介绍
Fitten Code AI（由非十科技提供）是面向开发团队的智能编程助手，它可以在本地和云端同时处理代码审核、测试建议、部署脚本生成等任务。本手册帮助 `abaco-loans-analytics` 仓库快速集成 Fitten Code AI，实现从开发到部署的全流程赋能。

## 安装教程
1. 准备基础环境：Git、Python 3.10+、Node.js（如需驱动前端项目）、Docker（可选，用于容器化）。
2. 将 Fitten Code AI 的模型与配置下载到安全存储，不要直接提交到 Git。根据组织策略，可以存放在 `/opt/fitten/models`、某个共享卷或模型服务器。
3. 在项目根目录创建 `fitten.config.toml`（或者组织指定的配置文件），并指向模型路径：

   ```toml
   [model]
   path = "/absolute/or/network/path/to/fitten-model"
   cache_dir = ".fitten/cache"
   ```

4. 安装 Fitten CLI 或 SDK（示例）：

   ```bash
   pip install fitten-cli
   fitten login        # 如需要身份认证
   ```

5. 将 Fitten 命令或脚本加入本地 `package.json` 的 `scripts`（Web）或 `Makefile`（分析）里，确保开发者可以一键触发。

## 功能介绍
- **即时代码分析**：在 PR、commit 或 CI 里自动运行，提供注释式反馈。
- **部署助手**：自动生成部署摘要、Azure 脚本、CI/CD 配置，降低运维门槛。
- **开发建议**：结合 `apps/web` 与 `apps/analytics` 项目，输出优化建议、测试覆盖率提示、模型性能评估。
- **多工具整合**：可以结合 GitHub Actions、Azure Pipelines 以及 Fitten 的本地 CLI，实现“开发—测试—部署—监控”闭环。

## 本地与 GitHub 集成建议
1. 本地：在开发者 shell 配置里定义 `FITTEN_CONFIG` 环境变量，让 Fitten CLI 拿到 `fitten.config.toml`。使用 `fitten sniff apps/web` 之类命令按需扫描子项目。
2. GitHub：在 `.github/workflows/` 中添加 `fitten.yml`，在 `pr` 与 `push` 触发 Fitten 检查，通知 Slack/Webhook。
3. 部署：Fitten 也可以生成 Azure、Vercel 等部署说明，结合 `infra/azure` 目录的脚本自动补全变量。
4. 机会（Opportunities）：适时恢复 Fitten output 到 Jira/Notion，形成可执行任务列表，确保“所有机会与工具”都能闭环。

## 常见问题
- **Q：Fitten 模型必须放在仓库里吗？**  
  A：不要提交模型文件。只需在 `fitten.config.toml` 中写入路径，必要时在 CI 里下载或挂载。
- **Q：如何调试 Fitten 生成的建议？**  
  A：在本地运行 `fitten explain <file>`，使用 `--preview` 查看上下文，并在 PR 里标记“是否采纳”。
- **Q：Fitten 与 SonarCloud、OpenAI 等如何协同？**  
  A：Fitten 可作为第一层审核，后续再触发 SonarCloud 的静态分析，OpenAI 用于复杂生成场景，互为补充。

## 联系我们
非十科技（Fitten Code）技术支持：  
- 官网： https://www.fittentech.com/  
- Fitten Code 平台： https://code.fittentech.com/  
- 通过平台内消息或企业邮箱获取授权与咨询。

## 常用链接
- Fitten Code 官网： https://code.fittentech.com/  
- 非十科技公司官网： https://www.fittentech.com/  
- `abaco-loans-analytics` 仓库（当前页面）： https://github.com/9nnxqzyq4y-eng/abaco-loans-analytics

## 测试本地推理
确保模型路径正确后，可以用 Hugging Face Transformers 快速验证 Fitten 本地推理：

```python
from transformers import AutoTokenizer, AutoModelForCausalLM

model_path = "/absolute/or/network/path/to/fitten-model"
tokenizer = AutoTokenizer.from_pretrained(model_path)
model = AutoModelForCausalLM.from_pretrained(model_path)

prompt = "Fitten Code AI 让编码更自信。"
inputs = tokenizer(prompt, return_tensors="pt")
outputs = model.generate(**inputs, max_new_tokens=64)
print(tokenizer.decode(outputs[0], skip_special_tokens=True))
```

如果模型不在本地，可通过 CI 下载（例如 `wget` + `unzip`），然后将路径传给 `huggingface` 接口或 Fitten CLI。这个运行示例只是为了确保模型可用、tokenizer 可读以及推理流程完整。
