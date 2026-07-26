import { tool } from "@opencode-ai/plugin"

export default tool({
  description: "Review Python code for quality and best practices",
  args: {
    file: tool.schema.string().describe("Path to the file to review"),
  },
  async execute(args, context) {
    const script = `${context.worktree}/.opencode/tools/review_code.py`
    const result = await Bun.$`python ${script} ${args.file}`.text()
    return result.trim()
  },
})
