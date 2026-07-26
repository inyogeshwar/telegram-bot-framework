import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Run security audit on Python files",
  args: {
    file: tool.schema.string().describe("Path to the file to audit"),
  },
  async execute(args, context) {
    const script = `${context.worktree}/.opencode/tools/security_audit.py`
    const result = await Bun.$`python ${script} ${args.file}`.text()
    return result.trim()
  },
})
